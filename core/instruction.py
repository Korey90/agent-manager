from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Instruction(BaseModel):
    """Represents a .github/instructions/*.md file — project-wide rules."""

    id: str = Field(default_factory=_uuid)
    name: str
    # Sections stored as ordered dict: section_title → content (str or list[str])
    sections: dict[str, str | list[str]] = Field(default_factory=dict)
    # Raw markdown (overrides sections if set; used when importing free-form files)
    raw_content: str = ""
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = _now()
