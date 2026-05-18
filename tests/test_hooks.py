from __future__ import annotations

from core.hook import Hook, HookEvent, HookType
from runtime.hook_runner import run_hooks


def test_hooks_run_in_priority_order():
    order = []

    import runtime.hook_runner as hr
    hr._BUILTINS["rec_a"] = lambda ctx: (order.append("a"), ctx)[1]
    hr._BUILTINS["rec_b"] = lambda ctx: (order.append("b"), ctx)[1]

    hooks = [
        Hook(name="b", event=HookEvent.PRE_RUN, type=HookType.BUILTIN, entrypoint="rec_b", priority=200),
        Hook(name="a", event=HookEvent.PRE_RUN, type=HookType.BUILTIN, entrypoint="rec_a", priority=100),
    ]
    run_hooks(hooks, HookEvent.PRE_RUN, {})
    assert order == ["a", "b"]


def test_disabled_hook_skipped():
    called = []
    import runtime.hook_runner as hr
    hr._BUILTINS["disabled_hook"] = lambda ctx: (called.append(1), ctx)[1]

    hooks = [
        Hook(name="h", event=HookEvent.PRE_RUN, type=HookType.BUILTIN,
             entrypoint="disabled_hook", enabled=False),
    ]
    run_hooks(hooks, HookEvent.PRE_RUN, {})
    assert called == []


def test_hook_context_passthrough():
    import runtime.hook_runner as hr
    hr._BUILTINS["upper_hook"] = lambda ctx: {**ctx, "input": ctx.get("input", "").upper()}

    hooks = [
        Hook(name="u", event=HookEvent.PRE_RUN, type=HookType.BUILTIN, entrypoint="upper_hook"),
    ]
    result = run_hooks(hooks, HookEvent.PRE_RUN, {"input": "hello"})
    assert result["input"] == "HELLO"
