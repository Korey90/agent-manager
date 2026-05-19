"""Persistent app settings — stored in ~/.agent-manager/settings.json"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_SETTINGS_DIR  = Path.home() / ".agent-manager"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"

_DEFAULTS: dict[str, Any] = {
    "language":      "pl",
    "default_model": "gpt-4o",
}

_data: dict[str, Any] = dict(_DEFAULTS)


def load() -> None:
    global _data
    _data = dict(_DEFAULTS)
    if _SETTINGS_FILE.exists():
        try:
            loaded = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
            _data.update(loaded)
        except Exception:
            pass


def save() -> None:
    _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(
        json.dumps(_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get(key: str, default: Any = None) -> Any:
    return _data.get(key, _DEFAULTS.get(key, default))


def put(key: str, value: Any) -> None:
    _data[key] = value
