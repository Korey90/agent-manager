from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from jinja2 import Environment, StrictUndefined, TemplateError
from pydantic import BaseModel, Field, model_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


_VARIABLE_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")

_jinja_env = Environment(undefined=StrictUndefined, autoescape=False)


class Prompt(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    content: str = ""
    variables: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _extract_variables(self) -> "Prompt":
        found = _VARIABLE_RE.findall(self.content)
        # preserve order, deduplicate
        seen: set[str] = set()
        unique = [v for v in found if not (v in seen or seen.add(v))]  # type: ignore[func-returns-value]
        self.variables = unique
        return self

    def render(self, **kwargs: Any) -> str:
        """Render prompt content with provided variables."""
        try:
            template = _jinja_env.from_string(self.content)
            return template.render(**kwargs)
        except TemplateError as exc:
            raise ValueError(f"Prompt render error: {exc}") from exc

    def touch(self) -> None:
        self.updated_at = _now()
        self.version += 1
