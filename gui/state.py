from __future__ import annotations
from pathlib import Path

_workspace: Path = Path(".")


def get_workspace() -> Path:
    return _workspace


def set_workspace(path: Path) -> None:
    global _workspace
    _workspace = path
    import registry as reg_module
    reg_module._registry = None


def get_registry():
    from registry import get_registry as _get
    return _get(_workspace / ".github")
