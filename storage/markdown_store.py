"""
MarkdownStore — stores Pydantic models as .md files in a directory.
Uses slug (filename without .md) as item ID.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from storage.store import BaseStore
from storage.markdown_utils import to_slug


T = type[BaseModel]


class MarkdownStore(BaseStore):
    """
    Each item is stored as `{directory}/{id}.md`.
    `renderer(item) -> str`  converts a model to markdown text.
    `parser(md, slug) -> dict` converts markdown + slug to a model dict.
    The model's `id` field is always the slug (filename).
    """

    def __init__(
        self,
        directory: Path,
        model_cls: type,
        renderer: Callable,
        parser: Callable,
    ) -> None:
        self._dir = directory
        self._model = model_cls
        self._renderer = renderer
        self._parser = parser
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, item_id: str) -> Path:
        return self._dir / f"{item_id}.md"

    def save(self, item: Any) -> None:
        md = self._renderer(item)
        self._path(item.id).write_text(md, encoding="utf-8")

    def get(self, item_id: str) -> Any | None:
        path = self._path(item_id)
        if not path.exists():
            return None
        md = path.read_text(encoding="utf-8")
        data = self._parser(md, item_id)
        return self._model.model_validate(data)

    def list(self) -> list[Any]:
        items = []
        for path in sorted(self._dir.glob("*.md")):
            slug = path.stem
            try:
                md = path.read_text(encoding="utf-8")
                data = self._parser(md, slug)
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

    def find_by_name(self, name: str) -> Any | None:
        slug = to_slug(name)
        item = self.get(slug)
        if item:
            return item
        # Fallback: scan all
        name_lower = name.lower()
        for item in self.list():
            if getattr(item, "name", "").lower() == name_lower:
                return item
        return None

    def get_or_raise(self, item_id: str, label: str = "item") -> Any:
        item = self.get(item_id) or self.find_by_name(item_id)
        if item is None:
            raise KeyError(f"{label} '{item_id}' not found")
        return item
