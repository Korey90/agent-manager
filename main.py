#!/usr/bin/env python
"""Agent Manager — entry point."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from cli.agent_cmd import app as agent_app
from cli.skill_cmd import app as skill_app
from cli.hook_cmd import app as hook_app
from cli.instruction_cmd import app as instruction_app

app = typer.Typer(
    name="agent-mgr",
    help="Create and manage VS Code Copilot agents, skills, hooks, and instructions.",
    no_args_is_help=True,
)
console = Console()

app.add_typer(agent_app, name="agent")
app.add_typer(skill_app, name="skill")
app.add_typer(hook_app, name="hook")
app.add_typer(instruction_app, name="instruction")


@app.command("scan")
def scan(
    workspace: Annotated[
        Path,
        typer.Argument(help="Path to project root containing .github/ folder"),
    ],
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
):
    """
    Scan an existing project's .github/ folder and import all agents, skills,
    hooks and instructions into the managed workspace.
    """
    from registry import get_registry
    from storage.markdown_utils import (
        agent_from_markdown, skill_from_markdown,
        hook_from_markdown, instruction_from_markdown, to_slug,
    )
    from core.agent import Agent
    from core.skill import Skill
    from core.hook import Hook
    from core.instruction import Instruction

    github_dir = workspace / ".github"
    if not github_dir.exists():
        console.print(f"[red]No .github/ folder found in {workspace}[/red]")
        raise typer.Exit(1)

    src_reg = get_registry(github_dir)
    dest_reg = get_registry()

    counts = {"agents": 0, "skills": 0, "hooks": 0, "instructions": 0}

    # Preview
    for kind, store_attr, model_cls, parser in [
        ("agents",       "agents",       Agent,       agent_from_markdown),
        ("skills",       "skills",       Skill,       skill_from_markdown),
        ("hooks",        "hooks",        Hook,        hook_from_markdown),
        ("instructions", "instructions", Instruction, instruction_from_markdown),
    ]:
        src_store = getattr(src_reg, store_attr)
        for path in sorted(src_store._dir.glob("*.md")):
            slug = path.stem
            name = slug.replace("-", " ").title()
            console.print(f"  [dim]{kind}[/dim]  [cyan]{name}[/cyan]  ({path.name})")
            counts[kind] += 1

    total = sum(counts.values())
    if total == 0:
        console.print("[yellow]Nothing to import.[/yellow]")
        return

    console.print(
        f"\nFound: [cyan]{counts['agents']}[/cyan] agents, "
        f"[green]{counts['skills']}[/green] skills, "
        f"[yellow]{counts['hooks']}[/yellow] hooks, "
        f"[magenta]{counts['instructions']}[/magenta] instructions"
    )

    if not yes:
        typer.confirm(f"Import all {total} items into current workspace?", abort=True)

    imported = 0
    for kind, src_store_attr, dest_store_attr, model_cls, parser in [
        ("agents",       "agents",       "agents",       Agent,       agent_from_markdown),
        ("skills",       "skills",       "skills",       Skill,       skill_from_markdown),
        ("hooks",        "hooks",        "hooks",        Hook,        hook_from_markdown),
        ("instructions", "instructions", "instructions", Instruction, instruction_from_markdown),
    ]:
        src_store = getattr(src_reg, src_store_attr)
        dest_store = getattr(dest_reg, dest_store_attr)
        for path in sorted(src_store._dir.glob("*.md")):
            slug = path.stem
            try:
                md = path.read_text(encoding="utf-8")
                data = parser(md, slug)
                item = model_cls.model_validate(data)
                dest_store.save(item)
                imported += 1
            except Exception as exc:
                console.print(f"[red]  Failed {path.name}: {exc}[/red]")

    console.print(f"\n[green]Imported {imported}/{total} items.[/green]")


if __name__ == "__main__":
    app()
