from __future__ import annotations

import json
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from core.skill import Skill, SkillType
from registry import get_registry

app = typer.Typer(help="Manage skills", no_args_is_help=True)
console = Console()


def _resolve(name_or_id: str) -> Skill:
    reg = get_registry()
    item = reg.skills.get(name_or_id) or reg.skills.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Skill '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    type: Annotated[SkillType, typer.Option("--type", "-t")] = SkillType.PYTHON,
    entrypoint: Annotated[str, typer.Option("--entrypoint", "-e")] = "",
    parameters: Annotated[str, typer.Option("--parameters")] = "{}",
):
    """Create a new skill."""
    reg = get_registry()
    if reg.skills.find_by_name(name):
        console.print(f"[yellow]Skill '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    try:
        params = json.loads(parameters)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON for --parameters: {exc}[/red]")
        raise typer.Exit(1)
    skill = Skill(name=name, description=description, type=type, entrypoint=entrypoint, parameters=params)
    reg.skills.save(skill)
    console.print(f"[green]Created skill '{name}' (id: {skill.id})[/green]")


@app.command("list")
def list_skills():
    """List all skills."""
    reg = get_registry()
    skills = reg.skills.list()
    if not skills:
        console.print("[dim]No skills found.[/dim]")
        return
    table = Table(title="Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Entrypoint")
    table.add_column("ID", style="dim")
    for s in skills:
        table.add_row(s.name, s.type.value, s.entrypoint or "—", s.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str):
    """Show details of a skill."""
    console.print_json(_resolve(name_or_id).model_dump_json(indent=2))


@app.command("edit")
def edit(
    name_or_id: str,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    entrypoint: Annotated[Optional[str], typer.Option("--entrypoint", "-e")] = None,
    parameters: Annotated[Optional[str], typer.Option("--parameters")] = None,
):
    """Edit an existing skill."""
    reg = get_registry()
    skill = _resolve(name_or_id)
    if description is not None:
        skill.description = description
    if entrypoint is not None:
        skill.entrypoint = entrypoint
    if parameters is not None:
        try:
            skill.parameters = json.loads(parameters)
        except json.JSONDecodeError as exc:
            console.print(f"[red]Invalid JSON: {exc}[/red]")
            raise typer.Exit(1)
    skill.touch()
    reg.skills.save(skill)
    console.print(f"[green]Skill '{skill.name}' updated.[/green]")


@app.command("delete")
def delete(name_or_id: str, yes: Annotated[bool, typer.Option("--yes", "-y")] = False):
    """Delete a skill."""
    skill = _resolve(name_or_id)
    if not yes:
        typer.confirm(f"Delete skill '{skill.name}'?", abort=True)
    get_registry().skills.delete(skill.id)
    console.print(f"[red]Deleted skill '{skill.name}'.[/red]")


@app.command("test")
def test(
    name_or_id: str,
    args: Annotated[str, typer.Option("--args", "-a", help="JSON args")] = "{}",
):
    """Test a skill with given arguments."""
    from runtime.skill_invoker import invoke_skill

    skill = _resolve(name_or_id)
    try:
        kwargs = json.loads(args)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid JSON: {exc}[/red]")
        raise typer.Exit(1)
    with console.status(f"Invoking skill '{skill.name}'..."):
        try:
            result = invoke_skill(skill, **kwargs)
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1)
    console.rule("Result")
    console.print(result)
