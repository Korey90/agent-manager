from __future__ import annotations

from pathlib import Path

from core.agent import Agent
from core.hook import Hook
from core.prompt import Prompt
from core.skill import Skill
from storage.store import JsonStore


class Registry:
    """Central access point for all stores."""

    def __init__(self, data_dir: Path) -> None:
        self.agents: JsonStore[Agent] = JsonStore(data_dir / "agents", Agent)
        self.skills: JsonStore[Skill] = JsonStore(data_dir / "skills", Skill)
        self.hooks: JsonStore[Hook] = JsonStore(data_dir / "hooks", Hook)
        self.prompts: JsonStore[Prompt] = JsonStore(data_dir / "prompts", Prompt)


_registry: Registry | None = None


def get_registry() -> Registry:
    global _registry
    if _registry is None:
        from config import DATA_DIR
        _registry = Registry(DATA_DIR)
    return _registry
