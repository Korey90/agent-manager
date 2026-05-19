from __future__ import annotations

import importlib
import subprocess
from typing import Any

import httpx

from core.skill import Skill, SkillType


def invoke_skill(skill: Skill, **kwargs: Any) -> Any:
    """Dispatch a skill call based on its type."""
    if not skill.entrypoint:
        return _invoke_guidance(skill, kwargs)
    match skill.type:
        case SkillType.PYTHON:
            return _invoke_python(skill, kwargs)
        case SkillType.API:
            return _invoke_api(skill, kwargs)
        case SkillType.SHELL:
            return _invoke_shell(skill, kwargs)
        case _:
            raise ValueError(f"Unknown skill type: {skill.type}")


def _invoke_guidance(skill: Skill, kwargs: dict[str, Any]) -> str:
    """Return skill description and steps as guidance text when no entrypoint is set."""
    parts: list[str] = []
    if skill.description:
        parts.append(f"Skill: {skill.name}\n{skill.description}")
    if skill.steps:
        steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(skill.steps))
        parts.append(f"Steps:\n{steps}")
    if skill.exit_criteria:
        parts.append(f"Exit criteria: {skill.exit_criteria}")
    if kwargs:
        import json
        parts.append(f"Arguments received: {json.dumps(kwargs, ensure_ascii=False)}")
    return "\n\n".join(parts) if parts else f"Skill '{skill.name}' executed."


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
