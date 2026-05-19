"""Session model — stores a single multi-turn conversation."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _sid() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


class SessionTurn(BaseModel):
    user_input: str
    agent_output: str
    model: str
    tool_calls: list[dict] = Field(default_factory=list)


class Session(BaseModel):
    id: str = Field(default_factory=_sid)
    agent_id: str
    agent_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turns: list[SessionTurn] = Field(default_factory=list)

    @property
    def label(self) -> str:
        """Short two-line display label for the sessions sidebar."""
        date = self.created_at[:16].replace("T", " ")
        first = self.turns[0].user_input[:55] if self.turns else "–"
        return f"[{self.agent_name}]  {date}\n{first}"
