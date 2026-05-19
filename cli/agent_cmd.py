from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.agent import Agent
from storage.markdown_utils import to_slug

app = typer.Typer(help="Manage agents (.github/agents/)", no_args_is_help=True)
console = Console()


def _get_reg(workspace: Optional[Path]):
    from registry import get_registry
    if workspace:
        return get_registry(workspace / ".github")
    return get_registry()


def _resolve(name_or_id: str, reg) -> Agent:
    item = reg.agents.get(to_slug(name_or_id)) or reg.agents.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Agent '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


_WS = Annotated[Optional[Path], typer.Option("--workspace", "-w", help="Project root (overrides WORKSPACE_DIR)")]


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt="Agent name")],
    role: Annotated[str, typer.Option("--role", "-r", prompt="Role (e.g. Senior Laravel Developer)")] = "",
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    workspace: _WS = None,
):
    """Create a new agent markdown file."""
    reg = _get_reg(workspace)
    slug = to_slug(name)
    if reg.agents.get(slug):
        console.print(f"[yellow]Agent '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    agent = Agent(id=slug, name=name, role=role, description=description)
    reg.agents.save(agent)
    console.print(f"[green]Created:[/green] {reg.agents._dir / slug}.md")


@app.command("list")
def list_agents(workspace: _WS = None):
    """List all agents."""
    reg = _get_reg(workspace)
    agents = reg.agents.list()
    if not agents:
        console.print("[dim]No agents found.[/dim]")
        return
    table = Table(title=f"Agents  ({reg.agents._dir})")
    table.add_column("Name", style="cyan")
    table.add_column("Role")
    table.add_column("Spec.", justify="right")
    table.add_column("Rules", justify="right")
    table.add_column("ID / slug", style="dim")
    for a in agents:
        table.add_row(
            a.name, a.role or "—",
            str(len(a.specialization)), str(len(a.hard_rules)),
            a.id,
        )
    console.print(table)


@app.command("show")
def show(name_or_id: str, workspace: _WS = None):
    """Show the rendered markdown of an agent."""
    from storage.markdown_utils import render_agent
    agent = _resolve(name_or_id, _get_reg(workspace))
    console.print(Panel(render_agent(agent), title=agent.name, border_style="cyan"))


@app.command("edit")
def edit(
    name_or_id: str,
    role: Annotated[Optional[str], typer.Option("--role", "-r")] = None,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    add_rule: Annotated[Optional[str], typer.Option("--add-rule")] = None,
    add_spec: Annotated[Optional[str], typer.Option("--add-specialization")] = None,
    add_pattern: Annotated[Optional[str], typer.Option("--add-pattern")] = None,
    workspace: _WS = None,
):
    """Edit fields of an agent."""
    reg = _get_reg(workspace)
    agent = _resolve(name_or_id, reg)
    if role is not None:
        agent.role = role
    if description is not None:
        agent.description = description
    if add_rule:
        agent.hard_rules.append(add_rule)
    if add_spec:
        agent.specialization.append(add_spec)
    if add_pattern:
        agent.preferred_patterns.append(add_pattern)
    agent.touch()
    reg.agents.save(agent)
    console.print(f"[green]Agent '{agent.name}' updated.[/green]")


@app.command("delete")
def delete(
    name_or_id: str,
    yes: Annotated[bool, typer.Option("--yes", "-y")] = False,
    workspace: _WS = None,
):
    """Delete an agent markdown file."""
    reg = _get_reg(workspace)
    agent = _resolve(name_or_id, reg)
    if not yes:
        typer.confirm(f"Delete agent '{agent.name}'?", abort=True)
    reg.agents.delete(agent.id)
    console.print(f"[red]Deleted agent '{agent.name}'.[/red]")


@app.command("import")
def import_file(
    file: Annotated[typer.FileText, typer.Argument(help="Path to existing .md agent file")],
    workspace: _WS = None,
):
    """Import an existing agent markdown file into the managed folder."""
    import os
    from storage.markdown_utils import agent_from_markdown
    reg = _get_reg(workspace)
    md = file.read()
    slug = to_slug(os.path.splitext(os.path.basename(file.name))[0])
    data = agent_from_markdown(md, slug)
    agent = Agent.model_validate(data)
    reg.agents.save(agent)
    console.print(f"[green]Imported '{agent.name}' → {reg.agents._dir / agent.id}.md[/green]")
