from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseStore(ABC, Generic[T]):
    @abstractmethod
    def save(self, item: T) -> None: ...

    @abstractmethod
    def get(self, item_id: str) -> T | None: ...

    @abstractmethod
    def list(self) -> list[T]: ...

    @abstractmethod
    def delete(self, item_id: str) -> bool: ...

    def get_or_raise(self, item_id: str, label: str = "item") -> T:
        item = self.get(item_id)
        if item is None:
            raise KeyError(f"{label} '{item_id}' not found")
        return item


class JsonStore(BaseStore[T]):
    """Stores each item as a separate JSON file inside a directory."""

    def __init__(self, directory: Path, model_cls: type[T]) -> None:
        self._dir = directory
        self._model = model_cls
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, item_id: str) -> Path:
        return self._dir / f"{item_id}.json"

    def save(self, item: T) -> None:
        path = self._path(item.id)  # type: ignore[attr-defined]
        path.write_text(item.model_dump_json(indent=2), encoding="utf-8")

    def get(self, item_id: str) -> T | None:
        path = self._path(item_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return self._model.model_validate(data)

    def list(self) -> list[T]:
        items = []
        for path in sorted(self._dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append(self._model.model_validate(data))
            except Exception:
                continue
        return items

    def delete(self, item_id: str) -> bool:
        path = self._path(item_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def find_by_name(self, name: str) -> T | None:
        """Return first item whose .name matches (case-insensitive)."""
        name_lower = name.lower()
        for item in self.list():
            if getattr(item, "name", "").lower() == name_lower:
                return item
        return None
