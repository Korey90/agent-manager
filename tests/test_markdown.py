from __future__ import annotations

import pytest
from storage.markdown_utils import (
    to_slug, from_slug, parse_title, parse_sections,
    render_agent, render_skill, render_hook,
    agent_from_markdown, skill_from_markdown, hook_from_markdown,
)
from core.agent import Agent
from core.skill import Skill
from core.hook import Hook


# ── Slug helpers ──────────────────────────────────────────────────────────────

def test_to_slug():
    assert to_slug("Backend Engineer") == "backend-engineer"
    assert to_slug("Laravel Action") == "laravel-action"


def test_from_slug():
    assert from_slug("backend-engineer") == "Backend Engineer"


# ── Parser ────────────────────────────────────────────────────────────────────

AGENT_MD = """\
# Backend Engineer

**Role:** Senior Laravel 13 Developer

**Specialization:**
- Clean Architecture & Action Pattern
- Filament 5 Admin Panel

**Hard Rules:**
- Controllers must be thin
- Always prefer Action classes
"""

def test_parse_title():
    assert parse_title(AGENT_MD) == "Backend Engineer"
    assert parse_title("# Skill: Test Gen") == "Test Gen"
    assert parse_title("# Hook: Pre Commit") == "Pre Commit"


def test_parse_sections_single_value():
    sections = parse_sections(AGENT_MD)
    assert sections.get("Role") == "Senior Laravel 13 Developer"


def test_parse_sections_list():
    sections = parse_sections(AGENT_MD)
    assert "Clean Architecture & Action Pattern" in sections["Specialization"]
    assert "Filament 5 Admin Panel" in sections["Specialization"]


def test_parse_sections_hard_rules():
    sections = parse_sections(AGENT_MD)
    assert "Controllers must be thin" in sections["Hard Rules"]


# ── Roundtrip: Agent ──────────────────────────────────────────────────────────

def test_agent_roundtrip():
    agent = Agent(
        id="backend-engineer",
        name="Backend Engineer",
        role="Senior Laravel Developer",
        specialization=["Action Pattern", "Filament"],
        hard_rules=["No logic in controllers"],
    )
    md = render_agent(agent)
    data = agent_from_markdown(md, "backend-engineer")
    restored = Agent.model_validate(data)

    assert restored.name == "Backend Engineer"
    assert restored.role == "Senior Laravel Developer"
    assert "Action Pattern" in restored.specialization
    assert "No logic in controllers" in restored.hard_rules


# ── Roundtrip: Skill ──────────────────────────────────────────────────────────

SKILL_MD = """\
# Skill: Laravel Action Implementation

**Description:** Create clean, reusable business logic using Action pattern.

**When to use:** Any non-trivial business operation.

**Steps:**
1. Identify anchor files
2. Create Action class
3. Run tests

**Template:**
```php
final class CreateLeadAction
{
    public function execute(): void {}
}
```
"""

def test_skill_roundtrip():
    data = skill_from_markdown(SKILL_MD, "laravel-action")
    skill = Skill.model_validate(data)
    assert skill.name == "Laravel Action Implementation"
    assert "Any non-trivial business operation" in skill.when_to_use
    assert len(skill.steps) == 3
    assert "CreateLeadAction" in skill.template
    assert skill.template_language == "php"

    md2 = render_skill(skill)
    data2 = skill_from_markdown(md2, "laravel-action")
    skill2 = Skill.model_validate(data2)
    assert skill2.steps == skill.steps


# ── Roundtrip: Hook ───────────────────────────────────────────────────────────

HOOK_MD = """\
# Hook: Pre-Commit

**Description:** Git pre-commit hook — protects code quality.

**Checks:**
- PHP Pint formatting
- ESLint + Prettier
- No hardcoded strings

**If any check fails:** block commit with clear message.
"""

def test_hook_roundtrip():
    data = hook_from_markdown(HOOK_MD, "pre-commit")
    hook = Hook.model_validate(data)
    assert hook.name == "Pre-Commit"
    assert "PHP Pint formatting" in hook.checks
    assert len(hook.checks) == 3


# ── MarkdownStore ─────────────────────────────────────────────────────────────

def test_markdown_store_save_and_get(tmp_path):
    from storage.markdown_store import MarkdownStore
    store = MarkdownStore(tmp_path / "agents", Agent, render_agent, agent_from_markdown)

    agent = Agent(id="test-agent", name="Test Agent", role="Tester")
    store.save(agent)
    assert (tmp_path / "agents" / "test-agent.md").exists()

    loaded = store.get("test-agent")
    assert loaded.name == "Test Agent"
    assert loaded.role == "Tester"


def test_markdown_store_list(tmp_path):
    from storage.markdown_store import MarkdownStore
    store = MarkdownStore(tmp_path / "agents", Agent, render_agent, agent_from_markdown)
    store.save(Agent(id="a", name="Alpha", role="R1"))
    store.save(Agent(id="b", name="Beta", role="R2"))
    items = store.list()
    assert len(items) == 2


def test_markdown_store_delete(tmp_path):
    from storage.markdown_store import MarkdownStore
    store = MarkdownStore(tmp_path / "agents", Agent, render_agent, agent_from_markdown)
    store.save(Agent(id="del-me", name="Del Me"))
    assert store.delete("del-me") is True
    assert store.get("del-me") is None


def test_markdown_store_find_by_name(tmp_path):
    from storage.markdown_store import MarkdownStore
    store = MarkdownStore(tmp_path / "agents", Agent, render_agent, agent_from_markdown)
    store.save(Agent(id="backend-engineer", name="Backend Engineer", role="Dev"))
    found = store.find_by_name("Backend Engineer")
    assert found is not None
    assert found.id == "backend-engineer"
