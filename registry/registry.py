from __future__ import annotations

from pathlib import Path

from core.agent import Agent
from core.hook import Hook
from core.instruction import Instruction
from core.prompt import Prompt
from core.skill import Skill
from storage.store import JsonStore
from storage.markdown_store import MarkdownStore
from storage.markdown_utils import (
    render_agent, agent_from_markdown,
    render_skill, skill_from_markdown,
    render_hook, hook_from_markdown,
    render_instruction, instruction_from_markdown,
)


class Registry:
    """
    Central access point for all stores.

    Primary stores target the .github/ folder (markdown format, VS Code Copilot compatible).
    Internal JSON stores in data/ hold runtime config (model, entrypoints, etc.).
    """

    def __init__(self, github_dir: Path, data_dir: Path) -> None:
        # ── Markdown stores (.github/ folder) ──────────────────────────────
        self.agents: MarkdownStore = MarkdownStore(
            github_dir / "agents", Agent, render_agent, agent_from_markdown
        )
        self.skills: MarkdownStore = MarkdownStore(
            github_dir / "skills", Skill, render_skill, skill_from_markdown
        )
        self.hooks: MarkdownStore = MarkdownStore(
            github_dir / "hooks", Hook, render_hook, hook_from_markdown
        )
        self.instructions: MarkdownStore = MarkdownStore(
            github_dir / "instructions", Instruction, render_instruction, instruction_from_markdown
        )
        # ── JSON store (runtime data — prompts, internal metadata) ──────────
        self.prompts: JsonStore[Prompt] = JsonStore(data_dir / "prompts", Prompt)


_registry: Registry | None = None


def get_registry(github_dir: Path | None = None) -> Registry:
    global _registry
    if github_dir is not None:
        # Per-call override (e.g. --workspace flag)
        from config import DATA_DIR
        return Registry(github_dir, DATA_DIR)
    if _registry is None:
        from config import GITHUB_DIR, DATA_DIR
        _registry = Registry(GITHUB_DIR, DATA_DIR)
    return _registry

