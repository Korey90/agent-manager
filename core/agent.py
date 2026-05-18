from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Agent(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    model: str = "gpt-4o"
    system_prompt_id: str | None = None
    skill_ids: list[str] = Field(default_factory=list)
    hook_ids: list[str] = Field(default_factory=list)
    enabled: bool = True
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _now()
