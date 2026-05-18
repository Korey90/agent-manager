from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from core.hook import Hook, HookEvent, HookType
from registry import get_registry

app = typer.Typer(help="Manage hooks", no_args_is_help=True)
console = Console()


def _resolve(name_or_id: str) -> Hook:
    reg = get_registry()
    item = reg.hooks.get(name_or_id) or reg.hooks.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Hook '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
    event: Annotated[HookEvent, typer.Option("--event", "-e", prompt=True)],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    type: Annotated[HookType, typer.Option("--type", "-t")] = HookType.PYTHON,
    entrypoint: Annotated[str, typer.Option("--entrypoint")] = "",
    priority: Annotated[int, typer.Option("--priority", "-p")] = 100,
):
    """Create a new hook."""
    reg = get_registry()
    if reg.hooks.find_by_name(name):
        console.print(f"[yellow]Hook '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    hook = Hook(
        name=name, description=description, event=event,
        type=type, entrypoint=entrypoint, priority=priority,
    )
    reg.hooks.save(hook)
    console.print(f"[green]Created hook '{name}' (id: {hook.id})[/green]")


@app.command("list")
def list_hooks():
    """List all hooks."""
    reg = get_registry()
    hooks = reg.hooks.list()
    if not hooks:
        console.print("[dim]No hooks found.[/dim]")
        return
    table = Table(title="Hooks")
    table.add_column("Name", style="cyan")
    table.add_column("Event")
    table.add_column("Type")
    table.add_column("Priority", justify="right")
    table.add_column("Enabled")
    table.add_column("ID", style="dim")
    for h in hooks:
        table.add_row(h.name, h.event.value, h.type.value, str(h.priority),
                      "✓" if h.enabled else "✗", h.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str):
    """Show details of a hook."""
    console.print_json(_resolve(name_or_id).model_dump_json(indent=2))


@app.command("edit")
def edit(
    name_or_id: str,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    entrypoint: Annotated[Optional[str], typer.Option("--entrypoint")] = None,
    priority: Annotated[Optional[int], typer.Option("--priority", "-p")] = None,
    enable: Annotated[Optional[bool], typer.Option("--enable/--disable")] = None,
):
    """Edit an existing hook."""
    reg = get_registry()
    hook = _resolve(name_or_id)
    if description is not None:
        hook.description = description
    if entrypoint is not None:
        hook.entrypoint = entrypoint
    if priority is not None:
        hook.priority = priority
    if enable is not None:
        hook.enabled = enable
    hook.touch()
    reg.hooks.save(hook)
    console.print(f"[green]Hook '{hook.name}' updated.[/green]")


@app.command("delete")
def delete(name_or_id: str, yes: Annotated[bool, typer.Option("--yes", "-y")] = False):
    """Delete a hook."""
    hook = _resolve(name_or_id)
    if not yes:
        typer.confirm(f"Delete hook '{hook.name}'?", abort=True)
    get_registry().hooks.delete(hook.id)
    console.print(f"[red]Deleted hook '{hook.name}'.[/red]")
