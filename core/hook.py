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


class HookEvent(str, Enum):
    PRE_RUN = "pre_run"
    POST_RUN = "post_run"
    ON_ERROR = "on_error"
    ON_SKILL_CALL = "on_skill_call"
    ON_RESPONSE = "on_response"


class HookType(str, Enum):
    PYTHON = "python"
    BUILTIN = "builtin"


class Hook(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    trigger: str = ""               # human-readable trigger description
    for_files: list[str] = Field(default_factory=list)   # glob patterns
    checks: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    on_failure: str = ""            # what to do on failure
    notes: list[str] = Field(default_factory=list)
    # Runtime settings
    event: HookEvent = HookEvent.PRE_RUN
    type: HookType = HookType.PYTHON
    entrypoint: str = ""
    priority: int = 100
    enabled: bool = True
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _now()
