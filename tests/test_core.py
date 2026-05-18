from __future__ import annotations

import pytest
from core.agent import Agent
from core.skill import Skill, SkillType
from core.hook import Hook, HookEvent, HookType
from core.prompt import Prompt


# ── Agent ─────────────────────────────────────────────────────────────────────

def test_agent_defaults():
    a = Agent(name="test")
    assert a.enabled is True
    assert a.skill_ids == []
    assert a.model == "gpt-4o"


def test_agent_touch_updates_updated_at():
    a = Agent(name="test")
    old = a.updated_at
    import time; time.sleep(0.01)
    a.touch()
    assert a.updated_at > old


# ── Skill ─────────────────────────────────────────────────────────────────────

def test_skill_defaults():
    s = Skill(name="ping")
    assert s.type == SkillType.PYTHON
    assert s.entrypoint == ""


# ── Hook ──────────────────────────────────────────────────────────────────────

def test_hook_event_values():
    assert HookEvent.PRE_RUN == "pre_run"
    assert HookEvent.POST_RUN == "post_run"


# ── Prompt ────────────────────────────────────────────────────────────────────

def test_prompt_extracts_variables():
    p = Prompt(name="t", content="Hello {{ name }}, you are {{ age }} years old.")
    assert p.variables == ["name", "age"]


def test_prompt_render():
    p = Prompt(name="t", content="Hi {{ name }}!")
    assert p.render(name="Jan") == "Hi Jan!"


def test_prompt_render_missing_variable():
    p = Prompt(name="t", content="Hi {{ name }}!")
    with pytest.raises(ValueError):
        p.render()


def test_prompt_version_bumps_on_touch():
    p = Prompt(name="t", content="x")
    assert p.version == 1
    p.touch()
    assert p.version == 2
