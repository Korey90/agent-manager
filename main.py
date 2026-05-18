#!/usr/bin/env python
"""Agent Manager — entry point."""

import typer

from cli.agent_cmd import app as agent_app
from cli.skill_cmd import app as skill_app
from cli.hook_cmd import app as hook_app
from cli.prompt_cmd import app as prompt_app

app = typer.Typer(
    name="agent-mgr",
    help="Create and manage AI agents, skills, hooks, and prompts.",
    no_args_is_help=True,
)

app.add_typer(agent_app, name="agent")
app.add_typer(skill_app, name="skill")
app.add_typer(hook_app, name="hook")
app.add_typer(prompt_app, name="prompt")


if __name__ == "__main__":
    app()
