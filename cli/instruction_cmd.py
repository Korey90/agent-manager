from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.instruction import Instruction
from storage.markdown_utils import to_slug

app = typer.Typer(help="Manage instructions (.github/instructions/)", no_args_is_help=True)
console = Console()

_WS = Annotated[Optional[Path], typer.Option("--workspace", "-w", help="Project root")]


def _get_reg(workspace: Optional[Path]):
    from registry import get_registry
    if workspace:
        return get_registry(workspace / ".github")
    return get_registry()


def _resolve(name_or_id: str, reg) -> Instruction:
    item = reg.instructions.get(to_slug(name_or_id)) or reg.instructions.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Instruction '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt="Instruction name")],
    content: Annotated[str, typer.Option("--content", "-c", prompt="Content (markdown)")] = "",
    workspace: _WS = None,
):
    """Create a new instruction markdown file."""
    reg = _get_reg(workspace)
    slug = to_slug(name)
    if reg.instructions.get(slug):
        console.print(f"[yellow]Instruction '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    instruction = Instruction(id=slug, name=name, raw_content=f"# {name}\n\n{content}")
    reg.instructions.save(instruction)
    console.print(f"[green]Created:[/green] {reg.instructions._dir / slug}.md")


@app.command("list")
def list_instructions(workspace: _WS = None):
    """List all instruction files."""
    reg = _get_reg(workspace)
    items = reg.instructions.list()
    if not items:
        console.print("[dim]No instructions found.[/dim]")
        return
    table = Table(title=f"Instructions  ({reg.instructions._dir})")
    table.add_column("Name", style="cyan")
    table.add_column("Size (chars)", justify="right")
    table.add_column("ID / slug", style="dim")
    for i in items:
        size = len(i.raw_content)
        table.add_row(i.name, str(size), i.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str, workspace: _WS = None):
    """Show the content of an instruction file."""
    inst = _resolve(name_or_id, _get_reg(workspace))
    console.print(Panel(inst.raw_content, title=inst.name, border_style="magenta"))


@app.command("delete")
def delete(
    name_or_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
    workspace: _WS = None,
):
    """Delete an instruction file."""
    reg = _get_reg(workspace)
    inst = _resolve(name_or_id, reg)
    if not yes:
        typer.confirm(f"Delete instruction '{inst.name}'?", abort=True)
    reg.instructions.delete(inst.id)
    console.print(f"[red]Deleted instruction '{inst.name}'.[/red]")


@app.command("import")
def import_file(
    file: Annotated[typer.FileText, typer.Argument(help="Path to .md instruction file")],
    workspace: _WS = None,
):
    """Import an existing instruction markdown file."""
    import os
    from storage.markdown_utils import instruction_from_markdown
    reg = _get_reg(workspace)
    md = file.read()
    slug = to_slug(os.path.splitext(os.path.basename(file.name))[0])
    data = instruction_from_markdown(md, slug)
    inst = Instruction.model_validate(data)
    reg.instructions.save(inst)
    console.print(f"[green]Imported '{inst.name}' → {reg.instructions._dir / inst.id}.md[/green]")
