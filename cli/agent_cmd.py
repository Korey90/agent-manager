from __future__ import annotations

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from core.agent import Agent
from registry import get_registry

app = typer.Typer(help="Manage agents", no_args_is_help=True)
console = Console()


def _resolve(name_or_id: str) -> Agent:
    reg = get_registry()
    item = reg.agents.get(name_or_id) or reg.agents.find_by_name(name_or_id)
    if item is None:
        console.print(f"[red]Agent '{name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    return item


@app.command("create")
def create(
    name: Annotated[str, typer.Option("--name", "-n", prompt=True)],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    model: Annotated[str, typer.Option("--model", "-m")] = "gpt-4o",
):
    """Create a new agent."""
    from config import DEFAULT_MODEL
    reg = get_registry()
    if reg.agents.find_by_name(name):
        console.print(f"[yellow]Agent '{name}' already exists.[/yellow]")
        raise typer.Exit(1)
    agent = Agent(name=name, description=description, model=model or DEFAULT_MODEL)
    reg.agents.save(agent)
    console.print(f"[green]Created agent '{name}' (id: {agent.id})[/green]")


@app.command("list")
def list_agents():
    """List all agents."""
    reg = get_registry()
    agents = reg.agents.list()
    if not agents:
        console.print("[dim]No agents found.[/dim]")
        return
    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Model")
    table.add_column("Skills", justify="right")
    table.add_column("Hooks", justify="right")
    table.add_column("Enabled")
    table.add_column("ID", style="dim")
    for a in agents:
        table.add_row(
            a.name, a.model,
            str(len(a.skill_ids)), str(len(a.hook_ids)),
            "✓" if a.enabled else "✗",
            a.id,
        )
    console.print(table)


@app.command("show")
def show(name_or_id: str):
    """Show details of an agent."""
    agent = _resolve(name_or_id)
    console.print_json(agent.model_dump_json(indent=2))


@app.command("edit")
def edit(
    name_or_id: str,
    description: Annotated[Optional[str], typer.Option("--description", "-d")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m")] = None,
    prompt_id: Annotated[Optional[str], typer.Option("--prompt")] = None,
    enable: Annotated[Optional[bool], typer.Option("--enable/--disable")] = None,
):
    """Edit an existing agent."""
    reg = get_registry()
    agent = _resolve(name_or_id)
    if description is not None:
        agent.description = description
    if model is not None:
        agent.model = model
    if prompt_id is not None:
        agent.system_prompt_id = prompt_id
    if enable is not None:
        agent.enabled = enable
    agent.touch()
    reg.agents.save(agent)
    console.print(f"[green]Agent '{agent.name}' updated.[/green]")


@app.command("delete")
def delete(name_or_id: str, yes: Annotated[bool, typer.Option("--yes", "-y")] = False):
    """Delete an agent."""
    agent = _resolve(name_or_id)
    if not yes:
        typer.confirm(f"Delete agent '{agent.name}'?", abort=True)
    get_registry().agents.delete(agent.id)
    console.print(f"[red]Deleted agent '{agent.name}'.[/red]")


@app.command("attach-skill")
def attach_skill(name_or_id: str, skill_name_or_id: str):
    """Attach a skill to an agent."""
    reg = get_registry()
    agent = _resolve(name_or_id)
    skill = reg.skills.get(skill_name_or_id) or reg.skills.find_by_name(skill_name_or_id)
    if skill is None:
        console.print(f"[red]Skill '{skill_name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    if skill.id not in agent.skill_ids:
        agent.skill_ids.append(skill.id)
        agent.touch()
        reg.agents.save(agent)
        console.print(f"[green]Skill '{skill.name}' attached to agent '{agent.name}'.[/green]")
    else:
        console.print("[yellow]Skill already attached.[/yellow]")


@app.command("detach-skill")
def detach_skill(name_or_id: str, skill_name_or_id: str):
    """Detach a skill from an agent."""
    reg = get_registry()
    agent = _resolve(name_or_id)
    skill = reg.skills.get(skill_name_or_id) or reg.skills.find_by_name(skill_name_or_id)
    if skill is None:
        console.print(f"[red]Skill '{skill_name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    if skill.id in agent.skill_ids:
        agent.skill_ids.remove(skill.id)
        agent.touch()
        reg.agents.save(agent)
        console.print(f"[green]Skill '{skill.name}' detached.[/green]")
    else:
        console.print("[yellow]Skill not attached.[/yellow]")


@app.command("attach-hook")
def attach_hook(name_or_id: str, hook_name_or_id: str):
    """Attach a hook to an agent."""
    reg = get_registry()
    agent = _resolve(name_or_id)
    hook = reg.hooks.get(hook_name_or_id) or reg.hooks.find_by_name(hook_name_or_id)
    if hook is None:
        console.print(f"[red]Hook '{hook_name_or_id}' not found.[/red]")
        raise typer.Exit(1)
    if hook.id not in agent.hook_ids:
        agent.hook_ids.append(hook.id)
        agent.touch()
        reg.agents.save(agent)
        console.print(f"[green]Hook '{hook.name}' attached to agent '{agent.name}'.[/green]")
    else:
        console.print("[yellow]Hook already attached.[/yellow]")


@app.command("run")
def run_cmd(
    name_or_id: str,
    input: Annotated[str, typer.Argument(help="User input / prompt")],
):
    """Run an agent with given input."""
    from runtime.runner import run_agent

    reg = get_registry()
    agent = _resolve(name_or_id)

    if not agent.enabled:
        console.print(f"[yellow]Agent '{agent.name}' is disabled.[/yellow]")
        raise typer.Exit(1)

    skills = [reg.skills.get_or_raise(sid, "skill") for sid in agent.skill_ids]
    hooks = [reg.hooks.get_or_raise(hid, "hook") for hid in agent.hook_ids]
    prompt = reg.prompts.get(agent.system_prompt_id) if agent.system_prompt_id else None

    with console.status(f"Running agent '{agent.name}'..."):
        result = run_agent(agent, input, skills=skills, hooks=hooks, system_prompt=prompt)

    if result.error:
        console.print(f"[red]Error:[/red] {result.error}")
        raise typer.Exit(1)

    console.rule("Output")
    console.print(result.output)

    if result.skill_calls:
        console.rule("Skill calls")
        for sc in result.skill_calls:
            console.print(f"  [cyan]{sc['skill']}[/cyan] → {sc['result']}")
