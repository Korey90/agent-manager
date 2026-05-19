from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class SkillPhase(str, Enum):
    GENERAL = "general"
    DEFINE  = "define"
    PLAN    = "plan"
    BUILD   = "build"
    VERIFY  = "verify"
    REVIEW  = "review"
    SHIP    = "ship"


class SkillType(str, Enum):
    PYTHON = "python"
    API = "api"
    SHELL = "shell"


class Skill(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    phase: SkillPhase = SkillPhase.GENERAL
    when_to_use: str = ""
    steps: list[str] = Field(default_factory=list)
    exit_criteria: str = ""
    rules: list[str] = Field(default_factory=list)
    anti_rationalizations: list[str] = Field(default_factory=list)
    template: str = ""          # code block content
    template_language: str = ""  # e.g. php, python, ts
    output_format: str = ""
    # Runtime settings
    type: SkillType = SkillType.PYTHON
    entrypoint: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)   # JSON Schema
    returns: dict[str, Any] = Field(default_factory=dict)       # JSON Schema
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _now()
