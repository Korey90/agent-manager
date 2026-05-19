# Agent Manager — v1.0.1

A desktop AI agent manager with a graphical interface (PyQt6).

## What problem does it solve?

Managing AI agents in a project quickly becomes chaotic — dozens of prompts, skills, hooks and rules scattered across files with no structure, no validation, no visualisation of relationships.

**Agent Manager** provides a graphical interface for:
- **defining agents** with a role, LLM model and a set of rules,
- **assigning procedures to them** (skills — steps, exit criteria, anti-rationalizations),
- **automatic actions** (hooks triggered by lifecycle events),
- **consistency validation** — detecting dead references and missing fields,
- **running agents** directly from the app (via litellm),
- **exporting** to `AGENTS.md` or `.cursor/rules/*.mdc` rules.

Everything saved as Markdown files in `.github/` — readable, versionable, and fully compatible with GitHub Copilot.

## Features

| Tab | Description |
|---|---|
| **🤖 Agents** | Create and edit agents: role, LLM model, assigned skills/hooks/instructions |
| **⚡ Skills** | Agent procedures: steps, phase, exit criteria, anti-rationalizations |
| **🔗 Hooks** | Automatic actions triggered by events (pre_run, post_run, on_error…) |
| **📋 Instructions** | General rules and guidelines for agents |
| **🗺 Diagram** | Visualisation of agent → skill → hook connections |
| **✅ Validation** | Quality issue review (missing fields, dead references) with click→panel navigation |
| **▶ Run** | Run an agent in the background (via litellm) with output preview, skill calls, active model, **session history** and **TTS speech synthesis** |
| **📤 Export** | Generate `AGENTS.md` or `.cursor/rules/*.mdc` rules |
| **⚙ Settings** | Interface language, default model, workspace, **API key management** (OpenAI / Anthropic / Gemini) |

### Additional features

- **Bilingual interface** — switch PL/EN on the fly (⚙ Settings → Language)
- **API keys in the GUI** — no need to manually edit `.env`; keys are stored in `~/.agent-manager/api_keys.env` and loaded on every startup
- **Save button always visible** — outside the scroll area, with ✔ Saved confirmation (green flash)
- **Tool name sanitization** — skill names with spaces or special characters are automatically converted to the format required by the OpenAI API (`^[a-zA-Z0-9_-]+$`)
- **Session history** — every conversation with an agent is automatically saved to `data/sessions/`; the sidebar lets you browse and resume previous sessions
- **TTS (Text-to-Speech)** — each agent response has a `▶` button for voice playback via OpenAI TTS (`tts-1`, voice `alloy`); the button indicates states: `▶` ready, `⏳` loading, `■` playing

---

## Requirements

- Python 3.12+
- PyQt6 >= 6.7.0
- pygame >= 2.5.0 (TTS playback)
- An LLM API key (OpenAI, Anthropic or any other supported by litellm)
- `OPENAI_API_KEY` required for the TTS feature

---

## Installation

```bash
git clone https://github.com/Korey90/agent-manager.git
cd agent-manager

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

### API Keys

API keys can be configured in two ways:

**Option A — via the GUI (recommended):** Launch the app, go to ⚙ **Settings → API Keys**, enter your keys and click *Save settings*. Keys are stored in `~/.agent-manager/api_keys.env` and loaded automatically on every startup.

**Option B — `.env` file:** Copy and fill in the environment file:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-...          # or ANTHROPIC_API_KEY, GEMINI_API_KEY
DEFAULT_MODEL=gpt-4o
WORKSPACE_DIR=.                # project directory containing .github/
DATA_DIR=data
```

---

## Running

```bash
python gui_main.py
```

Agent, skill and hook data is read from (and written to) the `.github/` directory pointed to by `WORKSPACE_DIR`.

---

## Project structure

```
agent-manager/
├── core/               # Pydantic models (Agent, Skill, Hook, Instruction, Prompt, Session)
│   └── session.py      # Session model (Session, SessionTurn) — conversation history
├── data/
│   └── sessions/       # Saved conversation sessions (JSON, auto-created)
├── gui/                # PyQt6 interface
│   ├── main_window.py  # Main window with tabs
│   ├── panels.py       # CRUD panels (BasePanel + AgentPanel, SkillPanel, …)
│   ├── run_panel.py    # Agent run tab (sessions, TTS)
│   ├── export_panel.py # Export tab (AGENTS.md / Cursor .mdc)
│   ├── diagram.py      # Graph visualisation
│   └── state.py        # Global state (workspace, registry)
├── runtime/            # Execution engine (litellm, hooks, skill invoker)
├── storage/            # Markdown file read/write
├── registry/           # Index of loaded objects
├── tests/              # pytest tests
├── gui_main.py         # GUI entry point
├── main.py             # CLI entry point
└── .env.example        # Example configuration
```

---

## Data model

### Agent
Has a role, description, LLM model and lists of assigned **skill_ids**, **hook_ids** and **instruction_ids**. Can contain `hard_rules` and `preferred_patterns`.

### Skill
Describes an agent procedure:
- `phase` — stage (general / define / plan / build / verify / review / ship)
- `steps` — list of steps to execute
- `exit_criteria` — completion condition
- `anti_rationalizations` — list of common excuses to avoid

### Hook
Automatic actions tied to lifecycle events (`pre_run`, `post_run`, `on_error`, `on_skill_call`, `on_response`). Contains a list of `checks` and `actions`.

---

## Validation

The **✅ Validation** panel detects, among others:
- a skill with no steps (error)
- missing `exit_criteria` or `when_to_use` (warning)
- an agent with no assigned skills
- references to non-existent skills/hooks

Every issue has a **⇗** button — clicking it navigates directly to the relevant panel and highlights the item with an orange border.

---

## Export

- **AGENTS.md** — a readable file with roles, models and rules for all agents
- **Cursor .mdc** — rules in `.cursor/rules/<agent_id>.mdc` format with YAML frontmatter and a full skill list

---

## Tests

```bash
python -m pytest tests/ -q
```

---

## Licence

MIT
