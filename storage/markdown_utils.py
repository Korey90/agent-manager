"""
Utilities for converting between Pydantic models and .github-compatible markdown files.

Format conventions:
  Agents  → .github/agents/{slug}.md
  Skills  → .github/skills/{slug}.md
  Hooks   → .github/hooks/{slug}.md
  Instructions → .github/instructions/{slug}.md
"""
from __future__ import annotations

import re
from pathlib import Path


# ── Slug helpers ──────────────────────────────────────────────────────────────

def to_slug(name: str) -> str:
    """'Backend Engineer' → 'backend-engineer'"""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug


def from_slug(slug: str) -> str:
    """'backend-engineer' → 'Backend Engineer'"""
    return slug.replace("-", " ").title()


# ── Markdown section parser ───────────────────────────────────────────────────

def parse_sections(md: str) -> dict[str, str | list[str]]:
    """
    Parse a markdown document into a dict of section_key → value.

    Handles:
      - `**Key:** single-line value`
      - `**Key:**\n- item\n- item`   (bullet list)
      - `**Key:**\n1. item\n2. item` (ordered list)
      - Code blocks after a section heading
    """
    sections: dict[str, str | list[str]] = {}
    lines = md.splitlines()
    i = 0
    current_key: str | None = None
    code_block_lines: list[str] | None = None
    code_lang = ""

    while i < len(lines):
        line = lines[i]

        # Code block start
        if line.strip().startswith("```"):
            code_lang = line.strip()[3:].strip()
            code_block_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_block_lines.append(lines[i])
                i += 1
            if current_key:
                sections[f"{current_key}__code"] = "\n".join(code_block_lines)
                sections[f"{current_key}__lang"] = code_lang
            i += 1
            continue

        # **Key:** value  or  **Key:**
        bold_match = re.match(r"^\*\*([^*]+)\*\*[:\s]*(.*)", line)
        if bold_match:
            key = bold_match.group(1).strip().rstrip(":")
            value = bold_match.group(2).strip()
            current_key = key
            if value:
                sections[key] = value
            else:
                # value may follow on next lines as a list
                pass
            i += 1
            continue

        # Bullet list item under current_key
        bullet_match = re.match(r"^[-*]\s+\[.\]\s+(.*)|^[-*]\s+(.*)", line)
        if bullet_match and current_key:
            item = (bullet_match.group(1) or bullet_match.group(2) or "").strip()
            if item:
                existing = sections.get(current_key)
                if isinstance(existing, list):
                    existing.append(item)
                elif isinstance(existing, str) and existing:
                    sections[current_key] = [existing, item]
                else:
                    sections[current_key] = [item]
            i += 1
            continue

        # Numbered list item
        num_match = re.match(r"^\d+\.\s+(.*)", line)
        if num_match and current_key:
            item = num_match.group(1).strip()
            existing = sections.get(current_key)
            if isinstance(existing, list):
                existing.append(item)
            elif isinstance(existing, str) and existing:
                sections[current_key] = [existing, item]
            else:
                sections[current_key] = [item]
            i += 1
            continue

        i += 1

    return sections


def parse_title(md: str) -> str:
    """Extract the `# Title` from markdown, stripping 'Skill: ' / 'Hook: ' prefixes."""
    for line in md.splitlines():
        m = re.match(r"^#+\s+(.*)", line)
        if m:
            title = m.group(1).strip()
            # Strip known prefixes
            for prefix in ("Skill: ", "Hook: ", "Instruction: "):
                if title.startswith(prefix):
                    title = title[len(prefix):]
            return title
    return ""


# ── Markdown renderers ────────────────────────────────────────────────────────

def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _numbered_list(items: list[str]) -> str:
    return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))


def _section(key: str, value: str | list[str] | None, ordered: bool = False) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return f"\n**{key}:** {value}\n"
    items = _numbered_list(value) if ordered else _bullet_list(value)
    return f"\n**{key}:**\n{items}\n"


def render_agent(agent) -> str:
    parts = [f"# {agent.name}\n"]
    if agent.role:
        parts.append(f"\n**Role:** {agent.role}\n")
    if agent.description:
        parts.append(f"\n**Description:** {agent.description}\n")
    if agent.hard_rules:
        parts.append(_section("Hard Rules", agent.hard_rules))
    if agent.specialization:
        parts.append(_section("Specialization", agent.specialization))
    if agent.responsibilities:
        parts.append(_section("Responsibilities", agent.responsibilities))
    if agent.preferred_patterns:
        parts.append(_section("Preferred Patterns", agent.preferred_patterns))
    if agent.notes:
        parts.append(_section("Notes", agent.notes))
    if agent.skill_ids:
        parts.append(_section("Skills", agent.skill_ids))
    if agent.hook_ids:
        parts.append(_section("Hooks", agent.hook_ids))
    if agent.instruction_ids:
        parts.append(_section("Instructions", agent.instruction_ids))
    return "".join(parts)


def render_skill(skill) -> str:
    parts = [f"# Skill: {skill.name}\n"]
    if skill.description:
        parts.append(f"\n**Description:** {skill.description}\n")
    phase = getattr(skill.phase, "value", str(skill.phase)) if getattr(skill, "phase", None) else "general"
    if phase and phase != "general":
        parts.append(f"\n**Phase:** {phase}\n")
    if skill.when_to_use:
        parts.append(f"\n**When to use:** {skill.when_to_use}\n")
    if skill.steps:
        parts.append(_section("Steps", skill.steps, ordered=True))
    if getattr(skill, "exit_criteria", ""):
        parts.append(f"\n**Exit criteria:** {skill.exit_criteria}\n")
    if skill.rules:
        parts.append(_section("Rules", skill.rules))
    if getattr(skill, "anti_rationalizations", []):
        parts.append(_section("Anti-rationalizations", skill.anti_rationalizations))
    if skill.output_format:
        parts.append(f"\n**Output format:** {skill.output_format}\n")
    if skill.template:
        lang = skill.template_language or ""
        parts.append(f"\n**Template:**\n```{lang}\n{skill.template}\n```\n")
    return "".join(parts)


def render_hook(hook) -> str:
    parts = [f"# Hook: {hook.name}\n"]
    if hook.description:
        parts.append(f"\n**Description:** {hook.description}\n")
    if hook.trigger:
        parts.append(f"\n**Trigger:** {hook.trigger}\n")
    if hook.for_files:
        parts.append(_section("For files in", hook.for_files))
    if hook.checks:
        parts.append(_section("Checks", hook.checks))
    if hook.actions:
        parts.append(_section("Actions", hook.actions, ordered=True))
    if hook.on_failure:
        parts.append(f"\n**On failure:** {hook.on_failure}\n")
    if hook.notes:
        parts.append(_section("Notes", hook.notes))
    return "".join(parts)


def render_instruction(instruction) -> str:
    if instruction.raw_content:
        return instruction.raw_content
    parts = [f"# {instruction.name}\n"]
    for key, value in instruction.sections.items():
        parts.append(_section(key, value))
    return "".join(parts)


# ── Model parsers ─────────────────────────────────────────────────────────────

def agent_from_markdown(md: str, slug: str) -> dict:
    from datetime import datetime, timezone
    title = parse_title(md)
    sections = parse_sections(md)

    def _list(key: str) -> list[str]:
        v = sections.get(key, [])
        return v if isinstance(v, list) else [v] if v else []

    def _str(key: str) -> str:
        v = sections.get(key, "")
        if isinstance(v, list):
            return " ".join(v)
        return v or ""

    return {
        "id": slug,
        "name": title or from_slug(slug),
        "role": _str("Role"),
        "description": _str("Description"),
        "specialization": _list("Specialization"),
        "responsibilities": _list("Responsibilities"),
        "hard_rules": _list("Hard Rules"),
        "preferred_patterns": _list("Preferred Patterns"),
        "notes": _list("Notes"),
        "skill_ids": _list("Skills"),
        "hook_ids": _list("Hooks"),
        "instruction_ids": _list("Instructions"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def skill_from_markdown(md: str, slug: str) -> dict:
    from datetime import datetime, timezone
    title = parse_title(md)
    sections = parse_sections(md)

    def _list(key: str) -> list[str]:
        v = sections.get(key, [])
        return v if isinstance(v, list) else [v] if v else []

    def _str(key: str) -> str:
        v = sections.get(key, "")
        if isinstance(v, list):
            return " ".join(v)
        return v or ""

    return {
        "id": slug,
        "name": title or from_slug(slug),
        "description": _str("Description"),
        "phase": _str("Phase") or "general",
        "when_to_use": _str("When to use"),
        "steps": _list("Steps"),
        "exit_criteria": _str("Exit criteria"),
        "rules": _list("Rules"),
        "anti_rationalizations": _list("Anti-rationalizations"),
        "template": sections.get("Template__code", ""),
        "template_language": sections.get("Template__lang", ""),
        "output_format": _str("Output format"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def hook_from_markdown(md: str, slug: str) -> dict:
    from datetime import datetime, timezone
    title = parse_title(md)
    sections = parse_sections(md)

    def _list(key: str) -> list[str]:
        v = sections.get(key, [])
        return v if isinstance(v, list) else [v] if v else []

    def _str(key: str) -> str:
        v = sections.get(key, "")
        if isinstance(v, list):
            return " ".join(v)
        return v or ""

    return {
        "id": slug,
        "name": title or from_slug(slug),
        "description": _str("Description"),
        "trigger": _str("Trigger"),
        "for_files": _list("For files in"),
        "checks": _list("Checks") or _list("Final validation checklist"),
        "actions": _list("Actions"),
        "on_failure": _str("On failure") or _str("If any check fails"),
        "notes": _list("Notes"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def instruction_from_markdown(md: str, slug: str) -> dict:
    from datetime import datetime, timezone
    title = parse_title(md)
    # Store as raw content — instructions are free-form
    content_lines = []
    skip_first_heading = True
    for line in md.splitlines():
        if skip_first_heading and re.match(r"^#\s+", line):
            skip_first_heading = False
            continue
        content_lines.append(line)
    return {
        "id": slug,
        "name": title or from_slug(slug),
        "raw_content": md,
        "sections": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
