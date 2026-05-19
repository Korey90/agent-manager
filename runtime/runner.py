from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import litellm

from core.agent import Agent
from core.hook import HookEvent
from core.skill import Skill
from core.hook import Hook
from core.prompt import Prompt
from runtime.hook_runner import run_hooks
from runtime.skill_invoker import invoke_skill


@dataclass
class RunResult:
    agent_id: str
    input: str
    output: str
    skill_calls: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def run_agent(
    agent: Agent,
    user_input: str,
    skills: list[Skill] | None = None,
    hooks: list[Hook] | None = None,
    system_prompt: Prompt | None = None,
) -> RunResult:
    skills = skills or []
    hooks = hooks or []

    # ── PRE_RUN hook ──────────────────────────────────────────────────────────
    context: dict[str, Any] = {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "input": user_input,
    }
    context = run_hooks(hooks, HookEvent.PRE_RUN, context)
    user_input = context.get("input", user_input)

    # ── build messages ────────────────────────────────────────────────────────
    system_content = system_prompt.content if system_prompt else agent.description
    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})
    messages.append({"role": "user", "content": user_input})

    # ── build tool definitions for LLM ───────────────────────────────────────
    tools = _build_tools(skills)

    skill_calls: list[dict[str, Any]] = []

    try:
        response = litellm.completion(
            model=agent.model,
            messages=messages,
            tools=tools if tools else None,
        )

        reply = response.choices[0].message

        # ── handle tool calls ─────────────────────────────────────────────────
        while reply.tool_calls:
            messages.append(reply)
            for tc in reply.tool_calls:
                skill = next((s for s in skills if _sanitize_tool_name(s.name) == tc.function.name), None)
                if skill is None:
                    tool_result = f"Skill '{tc.function.name}' not found."
                else:
                    import json
                    args = json.loads(tc.function.arguments or "{}")
                    # ON_SKILL_CALL hook
                    sc_ctx: dict[str, Any] = {"skill": tc.function.name, "args": args}
                    sc_ctx = run_hooks(hooks, HookEvent.ON_SKILL_CALL, sc_ctx)
                    args = sc_ctx.get("args", args)

                    tool_result = invoke_skill(skill, **args)
                    skill_calls.append({"skill": skill.name, "args": args, "result": tool_result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(tool_result),
                })

            response = litellm.completion(
                model=agent.model,
                messages=messages,
                tools=tools if tools else None,
            )
            reply = response.choices[0].message

        output = reply.content or ""

    except Exception as exc:
        # ── ON_ERROR hook ─────────────────────────────────────────────────────
        err_ctx: dict[str, Any] = {"agent_id": agent.id, "error": str(exc)}
        run_hooks(hooks, HookEvent.ON_ERROR, err_ctx)
        return RunResult(agent_id=agent.id, input=user_input, output="", error=str(exc))

    # ── POST_RUN / ON_RESPONSE hooks ──────────────────────────────────────────
    post_ctx: dict[str, Any] = {"agent_id": agent.id, "input": user_input, "output": output}
    post_ctx = run_hooks(hooks, HookEvent.POST_RUN, post_ctx)
    post_ctx = run_hooks(hooks, HookEvent.ON_RESPONSE, post_ctx)
    output = post_ctx.get("output", output)

    return RunResult(
        agent_id=agent.id,
        input=user_input,
        output=output,
        skill_calls=skill_calls,
    )


def _sanitize_tool_name(name: str) -> str:
    """Convert a skill name to a valid OpenAI function name (^[a-zA-Z0-9_-]+$)."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name).strip("_")
    return sanitized or "skill"


def _build_tools(skills: list[Skill]) -> list[dict[str, Any]]:
    tools = []
    for skill in skills:
        tools.append({
            "type": "function",
            "function": {
                "name": _sanitize_tool_name(skill.name),
                "description": skill.description,
                "parameters": skill.parameters or {"type": "object", "properties": {}},
            },
        })
    return tools
