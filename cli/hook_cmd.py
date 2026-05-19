from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.hook import Hook, HookEvent
from storage.markdown_utils import to_slug

app = typer.Typer(help="Manage hooks (.github/hooks/)", no_args_is_help=True)
console = Console()

_WS = Annotated[Optional[Path], typer.Option("--workspace", "-w", help="Project root")]


def _get_reg(workspace: Optional[Path]):
    from registry import get_registry
    if workspace:
        return get_registry(workspace / ".github")
    return get_registry()


def _resolve(name_or_id: str, reg) -> Hook:
    item = reg.hooks.get(to_slug(name_or_id)) or reg.hooks.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Hook '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt="Hook name")],
    description: Annotated[str, typer.Option("--description", "-d", prompt="Description")] = "",
    trigger: Annotated[str, typer.Option("--trigger", "-t")] = "",
    workspace: _WS = None,
):
    """Create a new hook markdown file."""
    reg = _get_reg(workspace)
    slug = to_slug(name)
    if reg.hooks.get(slug):
        console.print(f"[yellow]Hook '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    hook = Hook(id=slug, name=name, description=description, trigger=trigger)
    reg.hooks.save(hook)
    console.print(f"[green]Created:[/green] {reg.hooks._dir / slug}.md")


@app.command("list")
def list_hooks(workspace: _WS = None):
    """List all hooks."""
    reg = _get_reg(workspace)
    hooks = reg.hooks.list()
    if not hooks:
        console.print("[dim]No hooks found.[/dim]")
        return
    table = Table(title=f"Hooks  ({reg.hooks._dir})")
    table.add_column("Name", style="cyan")
    table.add_column("Trigger")
    table.add_column("Actions", justify="right")
    table.add_column("Checks", justify="right")
    table.add_column("ID / slug", style="dim")
    for h in hooks:
        table.add_row(h.name, h.trigger or "—", str(len(h.actions)), str(len(h.checks)), h.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str, workspace: _WS = None):
    """Show the rendered markdown of a hook."""
    from storage.markdown_utils import render_hook
    hook = _resolve(name_or_id, _get_reg(workspace))
    console.print(Panel(render_hook(hook), title=hook.name, border_style="yellow"))


@app.command("edit")
def edit(
    name_or_id: str,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    trigger: Annotated[Optional[str], typer.Option("--trigger", "-t")] = None,
    add_action: Annotated[Optional[str], typer.Option("--add-action")] = None,
    add_check: Annotated[Optional[str], typer.Option("--add-check")] = None,
    add_file: Annotated[Optional[str], typer.Option("--add-file", help="Add file glob pattern")] = None,
    on_failure: Annotated[Optional[str], typer.Option("--on-failure")] = None,
    workspace: _WS = None,
):
    """Edit an existing hook."""
    reg = _get_reg(workspace)
    hook = _resolve(name_or_id, reg)
    if description is not None:
        hook.description = description
    if trigger is not None:
        hook.trigger = trigger
    if add_action:
        hook.actions.append(add_action)
    if add_check:
        hook.checks.append(add_check)
    if add_file:
        hook.for_files.append(add_file)
    if on_failure is not None:
        hook.on_failure = on_failure
    hook.touch()
    reg.hooks.save(hook)
    console.print(f"[green]Hook '{hook.name}' updated.[/green]")


@app.command("delete")
def delete(
    name_or_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
    workspace: _WS = None,
):
    """Delete a hook markdown file."""
    reg = _get_reg(workspace)
    hook = _resolve(name_or_id, reg)
    if not yes:
        typer.confirm(f"Delete hook '{hook.name}'?", abort=True)
    reg.hooks.delete(hook.id)
    console.print(f"[red]Deleted hook '{hook.name}'.[/red]")


@app.command("import")
def import_file(
    file: Annotated[typer.FileText, typer.Argument(help="Path to existing .md hook file")],
    workspace: _WS = None,
):
    """Import an existing hook markdown file."""
    import os
    from storage.markdown_utils import hook_from_markdown
    reg = _get_reg(workspace)
    md = file.read()
    slug = to_slug(os.path.splitext(os.path.basename(file.name))[0])
    data = hook_from_markdown(md, slug)
    hook = Hook.model_validate(data)
    reg.hooks.save(hook)
    console.print(f"[green]Imported '{hook.name}' → {reg.hooks._dir / hook.id}.md[/green]")
