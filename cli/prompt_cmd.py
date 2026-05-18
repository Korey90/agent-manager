from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from core.prompt import Prompt
from registry import get_registry

app = typer.Typer(help="Manage prompts", no_args_is_help=True)
console = Console()


def _resolve(name_or_id: str) -> Prompt:
    reg = get_registry()
    item = reg.prompts.get(name_or_id) or reg.prompts.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Prompt '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
    content: Annotated[str, typer.Option("--content", "-c", prompt=True)],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    tags: Annotated[str, typer.Option("--tags", help="Comma-separated tags")] = "",
):
    """Create a new prompt template."""
    reg = get_registry()
    if reg.prompts.find_by_name(name):
        console.print(f"[yellow]Prompt '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    prompt = Prompt(name=name, description=description, content=content, tags=tag_list)
    reg.prompts.save(prompt)
    console.print(f"[green]Created prompt '{name}' (vars: {prompt.variables})[/green]")


@app.command("list")
def list_prompts():
    """List all prompts."""
    reg = get_registry()
    prompts = reg.prompts.list()
    if not prompts:
        console.print("[dim]No prompts found.[/dim]")
        return
    table = Table(title="Prompts")
    table.add_column("Name", style="cyan")
    table.add_column("Variables")
    table.add_column("Tags")
    table.add_column("Ver", justify="right")
    table.add_column("ID", style="dim")
    for p in prompts:
        table.add_row(p.name, ", ".join(p.variables) or "—",
                      ", ".join(p.tags) or "—", str(p.version), p.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str):
    """Show details of a prompt."""
    console.print_json(_resolve(name_or_id).model_dump_json(indent=2))


@app.command("edit")
def edit(
    name_or_id: str,
    content: Annotated[Optional[str], typer.Option("--content", "-c")] = None,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
):
    """Edit a prompt (bumps version)."""
    reg = get_registry()
    prompt = _resolve(name_or_id)
    if description is not None:
        prompt.description = description
    if content is not None:
        prompt.content = content
        # Re-validate to extract new variables
        prompt = Prompt.model_validate(prompt.model_dump())
    prompt.touch()
    reg.prompts.save(prompt)
    console.print(f"[green]Prompt '{prompt.name}' updated (v{prompt.version}).[/green]")


@app.command("delete")
def delete(name_or_id: str, yes: Annotated[bool, typer.Option("--yes", "-y")] = False):
    """Delete a prompt."""
    prompt = _resolve(name_or_id)
    if not yes:
        typer.confirm(f"Delete prompt '{prompt.name}'?", abort=True)
    get_registry().prompts.delete(prompt.id)
    console.print(f"[red]Deleted prompt '{prompt.name}'.[/red]")


@app.command("render")
def render(
    name_or_id: str,
    vars: Annotated[str, typer.Option("--vars", "-v", help='JSON variables, e.g. \'{"name":"Jan"}\'')] = "{}",
):
    """Render a prompt template with variables."""
    import json
    prompt = _resolve(name_or_id)
    try:
        kwargs = json.loads(vars)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON: {exc}[/red]")
        raise typer.Exit(1)
    try:
        rendered = prompt.render(**kwargs)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    console.rule("Rendered Prompt")
    console.print(rendered)


@app.command("import")
def import_prompt(
    file: Annotated[typer.FileText, typer.Argument(help="Path to .txt or .md file")],
    name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
):
    """Import a prompt from a text/markdown file."""
    reg = get_registry()
    content = file.read()
    if reg.prompts.find_by_name(name):
        console.print(f"[yellow]Prompt '{name}' already exists. Use edit instead.[/yellow]")
        raise typer.Exit(1)
    prompt = Prompt(name=name, content=content)
    reg.prompts.save(prompt)
    console.print(f"[green]Imported prompt '{name}' (vars: {prompt.variables})[/green]")
