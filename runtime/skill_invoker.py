from __future__ import annotations

import importlib
import subprocess
from typing import Any

import httpx

from core.skill import Skill, SkillType


def invoke_skill(skill: Skill, **kwargs: Any) -> Any:
    """Dispatch a skill call based on its type."""
    match skill.type:
        case SkillType.PYTHON:
            return _invoke_python(skill, kwargs)
        case SkillType.API:
            return _invoke_api(skill, kwargs)
        case SkillType.SHELL:
            return _invoke_shell(skill, kwargs)
        case _:
            raise ValueError(f"Unknown skill type: {skill.type}")


def _invoke_python(skill: Skill, kwargs: dict[str, Any]) -> Any:
    if not skill.entrypoint:
        raise ValueError(f"Skill '{skill.name}' has no entrypoint")
    module_path, _, func_name = skill.entrypoint.rpartition(".")
    if not module_path:
        raise ValueError(f"Invalid entrypoint '{skill.entrypoint}' — use 'module.function'")
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    return func(**kwargs)


def _invoke_api(skill: Skill, kwargs: dict[str, Any]) -> Any:
    if not skill.entrypoint:
        raise ValueError(f"Skill '{skill.name}' has no entrypoint (URL)")
    response = httpx.post(skill.entrypoint, json=kwargs, timeout=30)
    response.raise_for_status()
    return response.json()


def _invoke_shell(skill: Skill, kwargs: dict[str, Any]) -> Any:
    if not skill.entrypoint:
        raise ValueError(f"Skill '{skill.name}' has no entrypoint (command template)")
    cmd = skill.entrypoint.format(**kwargs)
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=30
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
