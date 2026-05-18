from __future__ import annotations

import importlib
from typing import Any

from core.hook import Hook, HookEvent, HookType


# ── built-in hooks ────────────────────────────────────────────────────────────

def _builtin_logger(context: dict[str, Any]) -> dict[str, Any]:
    import json
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] [HOOK:logger] {json.dumps(context, default=str, ensure_ascii=False)}")
    return context


_BUILTINS: dict[str, Any] = {
    "logger": _builtin_logger,
}


# ── dispatcher ────────────────────────────────────────────────────────────────

def run_hooks(
    hooks: list[Hook],
    event: HookEvent,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Run all hooks matching *event* in priority order.
    Each hook receives the context dict and must return the (possibly modified) context.
    """
    matching = sorted(
        (h for h in hooks if h.event == event and h.enabled),
        key=lambda h: h.priority,
    )
    for hook in matching:
        try:
            func = _resolve_hook(hook)
            result = func(context)
            if isinstance(result, dict):
                context = result
        except Exception as exc:
            print(f"[HOOK ERROR] hook '{hook.name}' ({event}): {exc}")
    return context


def _resolve_hook(hook: Hook):
    if hook.type == HookType.BUILTIN:
        name = hook.entrypoint or hook.name
        if name not in _BUILTINS:
            raise ValueError(f"Unknown built-in hook: '{name}'")
        return _BUILTINS[name]
    # PYTHON type
    module_path, _, func_name = hook.entrypoint.rpartition(".")
    if not module_path:
        raise ValueError(f"Invalid hook entrypoint '{hook.entrypoint}'")
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
