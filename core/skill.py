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


class SkillType(str, Enum):
    PYTHON = "python"
    API = "api"
    SHELL = "shell"


class Skill(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    type: SkillType = SkillType.PYTHON
    # python: "module.function", api: "https://...", shell: "command {arg}"
    entrypoint: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)   # JSON Schema
    returns: dict[str, Any] = Field(default_factory=dict)       # JSON Schema
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _now()
