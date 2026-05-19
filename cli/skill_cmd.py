from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.skill import Skill, SkillType
from storage.markdown_utils import to_slug

app = typer.Typer(help="Manage skills (.github/skills/)", no_args_is_help=True)
console = Console()

_WS = Annotated[Optional[Path], typer.Option("--workspace", "-w", help="Project root")]


def _get_reg(workspace: Optional[Path]):
    from registry import get_registry
    if workspace:
        return get_registry(workspace / ".github")
    return get_registry()


def _resolve(name_or_id: str, reg) -> Skill:
    item = reg.skills.get(to_slug(name_or_id)) or reg.skills.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Skill '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt="Skill name")],
    description: Annotated[str, typer.Option("--description", "-d", prompt="Description")] = "",
    when_to_use: Annotated[str, typer.Option("--when")] = "",
    workspace: _WS = None,
):
    """Create a new skill markdown file."""
    reg = _get_reg(workspace)
    slug = to_slug(name)
    if reg.skills.get(slug):
        console.print(f"[yellow]Skill '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    skill = Skill(id=slug, name=name, description=description, when_to_use=when_to_use)
    reg.skills.save(skill)
    console.print(f"[green]Created:[/green] {reg.skills._dir / slug}.md")


@app.command("list")
def list_skills(workspace: _WS = None):
    """List all skills."""
    reg = _get_reg(workspace)
    skills = reg.skills.list()
    if not skills:
        console.print("[dim]No skills found.[/dim]")
        return
    table = Table(title=f"Skills  ({reg.skills._dir})")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Steps", justify="right")
    table.add_column("ID / slug", style="dim")
    for s in skills:
        table.add_row(s.name, s.description[:60] or "—", str(len(s.steps)), s.id)
    console.print(table)


@app.command("show")
def show(name_or_id: str, workspace: _WS = None):
    """Show the rendered markdown of a skill."""
    from storage.markdown_utils import render_skill
    skill = _resolve(name_or_id, _get_reg(workspace))
    console.print(Panel(render_skill(skill), title=skill.name, border_style="green"))


@app.command("edit")
def edit(
    name_or_id: str,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    when_to_use: Annotated[Optional[str], typer.Option("--when")] = None,
    add_step: Annotated[Optional[str], typer.Option("--add-step")] = None,
    add_rule: Annotated[Optional[str], typer.Option("--add-rule")] = None,
    template: Annotated[Optional[str], typer.Option("--template")] = None,
    template_lang: Annotated[Optional[str], typer.Option("--template-lang")] = None,
    workspace: _WS = None,
):
    """Edit an existing skill."""
    reg = _get_reg(workspace)
    skill = _resolve(name_or_id, reg)
    if description is not None:
        skill.description = description
    if when_to_use is not None:
        skill.when_to_use = when_to_use
    if add_step:
        skill.steps.append(add_step)
    if add_rule:
        skill.rules.append(add_rule)
    if template is not None:
        skill.template = template
    if template_lang is not None:
        skill.template_language = template_lang
    skill.touch()
    reg.skills.save(skill)
    console.print(f"[green]Skill '{skill.name}' updated.[/green]")


@app.command("delete")
def delete(
    name_or_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
    workspace: _WS = None,
):
    """Delete a skill markdown file."""
    reg = _get_reg(workspace)
    skill = _resolve(name_or_id, reg)
    if not yes:
        typer.confirm(f"Delete skill '{skill.name}'?", abort=True)
    reg.skills.delete(skill.id)
    console.print(f"[red]Deleted skill '{skill.name}'.[/red]")


@app.command("import")
def import_file(
    file: Annotated[typer.FileText, typer.Argument(help="Path to existing .md skill file")],
    workspace: _WS = None,
):
    """Import an existing skill markdown file."""
    import os
    from storage.markdown_utils import skill_from_markdown
    reg = _get_reg(workspace)
    md = file.read()
    slug = to_slug(os.path.splitext(os.path.basename(file.name))[0])
    data = skill_from_markdown(md, slug)
    skill = Skill.model_validate(data)
    reg.skills.save(skill)
    console.print(f"[green]Imported '{skill.name}' → {reg.skills._dir / skill.id}.md[/green]")
