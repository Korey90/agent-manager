"""Internationalization — Polish (pl) and English (en) strings."""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

# ─────────────────────────────────────────────────────────────────────────────

_STRINGS: dict[str, dict[str, str]] = {
    "pl": {
        # Tabs
        "tab.agents":       "🤖  Agenci",
        "tab.skills":       "⚡  Skille",
        "tab.hooks":        "🔗  Hooki",
        "tab.instructions": "📋  Instrukcje",
        "tab.diagram":      "🗺  Diagram",
        "tab.validation":   "✅  Walidacja",
        "tab.run":          "▶  Uruchom",
        "tab.export":       "📤  Eksport",
        "tab.settings":     "⚙  Ustawienia",
        # Menu
        "menu.file":                "Plik",
        "menu.help":                "Pomoc",
        "action.change_workspace":  "Zmień workspace…",
        "action.scan":              "Skanuj .github/…",
        "action.quit":              "Zamknij",
        "action.about":             "O programie…",
        # Toolbar
        "toolbar.workspace": "📂 Workspace",
        "toolbar.scan":      "⬇ Skanuj .github/",
        "toolbar.refresh":   "↺ Odśwież",
        # Common buttons
        "btn.new":    "＋ Nowy",
        "btn.delete": "✕ Usuń",
        "btn.save":   "💾  Zapisz",
        "btn.cancel": "Anuluj",
        "btn.refresh": "↻ Odśwież",
        "btn.run":    "▶  Uruchom",
        "btn.stop":   "✕  Anuluj",
        "btn.copy":   "Kopiuj",
        "btn.export": "📤  Eksportuj",
        # Panels — Agent
        "agent.form_title":         "Agent",
        "agent.name":               "Nazwa",
        "agent.role":               "Rola",
        "agent.description":        "Opis",
        "agent.model":              "Model LLM",
        "agent.specialization":     "Specjalizacja",
        "agent.responsibilities":   "Obowiązki",
        "agent.hard_rules":         "Twarde zasady (Hard Rules)",
        "agent.preferred_patterns": "Preferowane wzorce",
        "agent.notes":              "Notatki",
        "agent.skills":             "Skille agenta",
        "agent.hooks":              "Hooki agenta",
        "agent.instructions":       "Instrukcje agenta",
        "agent.spec_ph":            "Dodaj specjalizację…",
        "agent.resp_ph":            "Dodaj obowiązek…",
        "agent.rules_ph":           "Dodaj zasadę…",
        "agent.pat_ph":             "Dodaj wzorzec…",
        "agent.notes_ph":           "Dodaj notatkę…",
        # Banners info
        "agent.banner": (
            "<b>Agent</b> to samodzielna jednostka AI ze zdefiniowaną rolą, modelem LLM i zestawem skilli. "
            "Każdy agent jest zapisywany jako plik <code>.github/agents/&lt;id&gt;.md</code>. "
            "Przypisz skille (checkboxy poniżej), by agent wiedział, z jakich narzędzi korzystać."
        ),
        "skill.banner": (
            "<b>Skill</b> to workflow kroków z jasnymi <i>exit criteria</i> (wg Agent Skills). "
            "Dodaj fazę SDLC, kroki (Steps), warunek ukończenia (Exit Criteria), zasady i "
            "<i>anti-rationalizations</i> — rebuttals do wymówek, które agent może podać żeby pominąć workflow. "
            "Plik: <code>.github/skills/&lt;id&gt;.md</code>."
        ),
        "skill.banner_exit": (
            "⬛ <b>Exit criteria</b> — opisz konkretny, weryfikowalny warunek ukończenia zadania. "
            "Np. <i>\"testy przechodzą, build jest czysty, reviewer zaakceptował\"</i>. "
            "Bez tego agent nie wie kiedy zadanie jest naprawdę skończone."
        ),
        "skill.banner_anti": (
            "🔄 <b>Anti-rationalizations</b> — rebuttals do wymówek agenta. "
            "Format: <i>wymówka | odpowiedź</i>, np. "
            "<i>\"This is too simple for a spec | Acceptance criteria still apply.\"</i>"
        ),
        "hook.banner": (
            "<b>Hook</b> to akcja automatycznie wyzwalana przez zdarzenie w cyklu życia agenta. "
            "Ustaw <i>wyzwalacz</i> (np. pre-commit, on-save), <i>zdarzenie</i> (pre_run / post_run / on_error) "
            "i <i>typ</i> (python = skrypt, builtin = wbudowana funkcja). "
            "Pliki hooków: <code>.github/hooks/&lt;id&gt;.md</code>."
        ),
        "instr.banner": (
            "<b>Instruction</b> to zestaw reguł i wytycznych dla Copilota — np. konwencje kodowania, "
            "zakazane wzorce lub kontekst projektu. Pole <i>applyTo</i> (glob) decyduje, "
            "do jakich plików instrukcja jest dołączana (np. <code>**/*.ts</code> tylko dla TypeScriptu). "
            "Plik zapisywany w <code>.github/instructions/&lt;id&gt;.md</code> z YAML frontmatter."
        ),
        "run.banner": (
            "<b>Uruchamianie agenta</b> — wybierz agenta, wpisz zadanie i kliknij <b>Uruchom</b>. "
            "Wywołanie przebiega przez <code>runtime/runner.py</code> (litellm). "
            "Wymagany klucz API np. <code>OPENAI_API_KEY</code> lub <code>ANTHROPIC_API_KEY</code> "
            "ustawiony jako zmienna środowiskowa."
        ),
        "export.banner": (
            "<b>Eksport</b> — wygeneruj pliki konfiguracyjne dla zewnętrznych narzędzi AI. "
            "<b>AGENTS.md</b> to opis dla GitHub Copilot (główny folder projektu); "
            "<b>Cursor</b> zapisuje <code>.cursor/rules/&lt;id&gt;.mdc</code> dla Cursor IDE. "
            "Podgląd aktualizuje się na bieżąco po wyborze agenta i formatu."
        ),
        "diagram.banner": (
            "<b>Diagram</b> wizualizuje powiązania agenta ze skillami i hookami. "
            "<i>Zależności</i> — widok gwiaźdowy (agent w centrum). "
            "<i>Workflow</i> — przepływ: START → pre-hooki → agent → skille → post-hooki → END. "
            "Kółko myszy = zoom  ·  przeciągnij = przesunięcie."
        ),
        # Panels — Skill / Hook / Instruction
        "skill.form_title":     "Skill",
        "skill.name":           "Nazwa",
        "skill.description":    "Opis",
        "skill.phase":          "Faza SDLC",
        "skill.when_to_use":    "Kiedy użyć",
        "skill.steps":          "Kroki (Steps)",
        "skill.exit_criteria":  "Exit Criteria",
        "skill.rules":          "Zasady (Rules)",
        "skill.anti":           "Anti-rationalizations",
        "skill.lang":           "Język szablonu",
        "skill.output_format":  "Format wyjścia",
        "skill.template":       "Szablon kodu (Template)",
        "skill.steps_ph":       "Dodaj krok…",
        "skill.rules_ph":       "Dodaj zasadę…",
        "skill.anti_ph":        "Dodaj: wymówka | obalenie…",
        # Panels — Hook
        "hook.form_title":  "Hook",
        "hook.name":        "Nazwa",
        "hook.description": "Opis",
        "hook.trigger":     "Wyzwalacz",
        "hook.on_failure":  "Przy błędzie",
        "hook.event":       "Zdarzenie (event)",
        "hook.type":        "Typ",
        "hook.priority":    "Priorytet",
        "hook.for_files":   "Pliki (For files in)",
        "hook.checks":      "Sprawdzenia (Checks)",
        "hook.actions":     "Akcje (Actions)",
        "hook.notes":       "Notatki",
        "hook.trigger_ph":  "Wybierz lub wpisz wyzwalacz…",
        "hook.files_ph":    "Dodaj wzorzec pliku…",
        "hook.checks_ph":   "Dodaj sprawdzenie…",
        "hook.actions_ph":  "Dodaj akcję…",
        "hook.notes_ph":    "Dodaj notatkę…",
        # Panels — Instruction
        "instr.form_title":  "Instrukcja / Rules",
        "instr.name":        "Nazwa",
        "instr.apply_to":    "applyTo (glob)",
        "instr.sections":    "Sekcje",
        "instr.add_section": "＋ Dodaj sekcję…",
        # Validation
        "valid.agents_hdr":  "Agenci",
        "valid.issues_hdr":  "Problemy",
        "valid.all":         "🔍 Wszystkie",
        "valid.run":         "↻ Odśwież",
        "valid.hint":        "🔴 błąd  🟡 ostrzeżenie  🟢 OK",
        "valid.ok":          "✅  Wszystko OK — brak problemów.",
        # Run panel
        "run.agent_lbl":   "Agent:",
        "run.task_lbl":    "Zadanie / prompt:",
        "run.input_ph":    "Wpisz zadanie dla agenta…",
        "run.output_lbl":  "Wynik:",
        "run.output_ph":   "Tutaj pojawi się odpowiedź agenta…",
        # Export panel
        "export.agent_lbl":   "Agent:",
        "export.fmt_lbl":     "Format:",
        "export.preview_lbl": "Podgląd:",
        "export.all":         "Wszystkie agenty",
        # Settings panel
        "settings.title":           "Ustawienia",
        "settings.section_general": "Ogólne",
        "settings.language":        "Język interfejsu:",
        "settings.lang_pl":         "Polski",
        "settings.lang_en":         "English",
        "settings.model":           "Domyślny model LLM:",
        "settings.workspace":       "Workspace:",
        "settings.ws_browse":       "Przeglądaj…",
        "settings.save":            "Zapisz ustawienia",
        "settings.saved":           "✅  Ustawienia zapisane.",
        "btn.saved":                "✔ Zapisano",
        "settings.hint":            "Zmiana języka jest natychmiastowa — etykiety odświeżają się automatycznie.",
        # API Keys section
        "settings.section_api":     "Klucze API",
        "settings.api_hint":        "Klucze są przechowywane lokalnie w <code>~/.agent-manager/api_keys.env</code> i nie trafiają do repozytorium.",
        "settings.api_show":        "Pokaż",
        "settings.api_hide":        "Ukryj",
        # Dialogs
        "dlg.new_title":   "Nowy {kind}",
        "dlg.new_label":   "Nazwa:",
        "dlg.exists":      "Już istnieje",
        "dlg.exists_msg":  "{kind} o nazwie '{name}' już istnieje.",
        "dlg.delete":      "Usuń",
        "dlg.delete_q":    "Usunąć '{name}'?",
        "dlg.no_select":   "Brak wyboru",
        "dlg.no_select_m": "Wybierz element z listy.",
        # About
        "about.title": "O programie",
        "about.body": (
            "<h3>Agent Manager <small style='color:#666'>v{ver}</small></h3>"
            "<p><b>Jaki problem rozwiązuje?</b><br>"
            "Zarządzanie agentami AI w projekcie szybko staje się chaotyczne — "
            "dziesiątki promptów, skilli, hooków i reguł rozrzucone w plikach bez struktury. "
            "Agent Manager daje graficzny interfejs do definiowania agentów, przypisywania im "
            "procedur (skille) i automatycznych akcji (hooki), walidacji spójności "
            "i uruchamiania ich bezpośrednio z poziomu aplikacji — wszystko zapisane "
            "jako pliki Markdown w <code>.github/</code>, czytelne dla GitHub Copilot.</p>"
            "<p><b>Obsługiwane modele:</b> OpenAI, Anthropic, Google Gemini "
            "(i każdy inny obsługiwany przez litellm).</p>"
            "<p><b>Repozytorium:</b> "
            "<a href='https://github.com/Korey90/agent-manager'>"
            "github.com/Korey90/agent-manager</a></p>"
        ),
    },
    "en": {
        # Tabs
        "tab.agents":       "🤖  Agents",
        "tab.skills":       "⚡  Skills",
        "tab.hooks":        "🔗  Hooks",
        "tab.instructions": "📋  Instructions",
        "tab.diagram":      "🗺  Diagram",
        "tab.validation":   "✅  Validation",
        "tab.run":          "▶  Run",
        "tab.export":       "📤  Export",
        "tab.settings":     "⚙  Settings",
        # Menu
        "menu.file":                "File",
        "menu.help":                "Help",
        "action.change_workspace":  "Change workspace…",
        "action.scan":              "Scan .github/…",
        "action.quit":              "Quit",
        "action.about":             "About…",
        # Toolbar
        "toolbar.workspace": "📂 Workspace",
        "toolbar.scan":      "⬇ Scan .github/",
        "toolbar.refresh":   "↺ Refresh",
        # Common buttons
        "btn.new":    "＋ New",
        "btn.delete": "✕ Delete",
        "btn.save":   "💾  Save",
        "btn.cancel": "Cancel",
        "btn.refresh": "↻ Refresh",
        "btn.run":    "▶  Run",
        "btn.stop":   "✕  Cancel",
        "btn.copy":   "Copy",
        "btn.export": "📤  Export",
        # Panels — Agent
        "agent.form_title":         "Agent",
        "agent.name":               "Name",
        "agent.role":               "Role",
        "agent.description":        "Description",
        "agent.model":              "LLM Model",
        "agent.specialization":     "Specialization",
        "agent.responsibilities":   "Responsibilities",
        "agent.hard_rules":         "Hard Rules",
        "agent.preferred_patterns": "Preferred Patterns",
        "agent.notes":              "Notes",
        "agent.skills":             "Agent Skills",
        "agent.hooks":              "Agent Hooks",
        "agent.instructions":       "Agent Instructions",
        "agent.spec_ph":            "Add specialization…",
        "agent.resp_ph":            "Add responsibility…",
        "agent.rules_ph":           "Add rule…",
        "agent.pat_ph":             "Add pattern…",
        "agent.notes_ph":           "Add note…",
        # Banners info
        "agent.banner": (
            "<b>Agent</b> is a standalone AI unit with a defined role, LLM model and a set of skills. "
            "Each agent is saved as <code>.github/agents/&lt;id&gt;.md</code>. "
            "Assign skills (checkboxes below) so the agent knows which tools to use."
        ),
        "skill.banner": (
            "<b>Skill</b> is a step-by-step workflow with clear <i>exit criteria</i> (per Agent Skills methodology). "
            "Add an SDLC phase, steps, completion condition (Exit Criteria), rules and "
            "<i>anti-rationalizations</i> — rebuttals to excuses the agent might give to skip the workflow. "
            "File: <code>.github/skills/&lt;id&gt;.md</code>."
        ),
        "skill.banner_exit": (
            "⬛ <b>Exit criteria</b> — describe a concrete, verifiable completion condition. "
            "E.g. <i>\"tests pass, build is clean, reviewer approved\"</i>. "
            "Without this the agent doesn't know when the task is truly done."
        ),
        "skill.banner_anti": (
            "🔄 <b>Anti-rationalizations</b> — rebuttals to agent excuses. "
            "Format: <i>excuse | rebuttal</i>, e.g. "
            "<i>\"This is too simple for a spec | Acceptance criteria still apply.\"</i>"
        ),
        "hook.banner": (
            "<b>Hook</b> is an action automatically triggered by an event in the agent lifecycle. "
            "Set the <i>trigger</i> (e.g. pre-commit, on-save), <i>event</i> (pre_run / post_run / on_error) "
            "and <i>type</i> (python = script, builtin = built-in function). "
            "Hook files: <code>.github/hooks/&lt;id&gt;.md</code>."
        ),
        "instr.banner": (
            "<b>Instruction</b> is a set of rules and guidelines for Copilot — e.g. coding conventions, "
            "forbidden patterns or project context. The <i>applyTo</i> field (glob) controls "
            "which files the instruction applies to (e.g. <code>**/*.ts</code> for TypeScript only). "
            "Saved in <code>.github/instructions/&lt;id&gt;.md</code> with YAML frontmatter."
        ),
        "run.banner": (
            "<b>Run Agent</b> — select an agent, enter a task and click <b>Run</b>. "
            "Execution goes through <code>runtime/runner.py</code> (litellm). "
            "An API key such as <code>OPENAI_API_KEY</code> or <code>ANTHROPIC_API_KEY</code> "
            "must be set as an environment variable."
        ),
        "export.banner": (
            "<b>Export</b> — generate config files for external AI tools. "
            "<b>AGENTS.md</b> is a description for GitHub Copilot (project root); "
            "<b>Cursor</b> writes <code>.cursor/rules/&lt;id&gt;.mdc</code> for Cursor IDE. "
            "The preview updates live when you pick an agent and format."
        ),
        "diagram.banner": (
            "<b>Diagram</b> visualises the agent's connections to skills and hooks. "
            "<i>Dependencies</i> — star view (agent at centre). "
            "<i>Workflow</i> — flow: START → pre-hooks → agent → skills → post-hooks → END. "
            "Scroll wheel = zoom  ·  drag = pan."
        ),
        # Panels — Skill / Hook / Instruction
        "skill.form_title":     "Skill",
        "skill.name":           "Name",
        "skill.description":    "Description",
        "skill.phase":          "SDLC Phase",
        "skill.when_to_use":    "When to use",
        "skill.steps":          "Steps",
        "skill.exit_criteria":  "Exit Criteria",
        "skill.rules":          "Rules",
        "skill.anti":           "Anti-rationalizations",
        "skill.lang":           "Template language",
        "skill.output_format":  "Output format",
        "skill.template":       "Code Template",
        "skill.steps_ph":       "Add step…",
        "skill.rules_ph":       "Add rule…",
        "skill.anti_ph":        "Add: excuse | rebuttal…",
        # Panels — Hook
        "hook.form_title":  "Hook",
        "hook.name":        "Name",
        "hook.description": "Description",
        "hook.trigger":     "Trigger",
        "hook.on_failure":  "On failure",
        "hook.event":       "Event",
        "hook.type":        "Type",
        "hook.priority":    "Priority",
        "hook.for_files":   "For files (glob)",
        "hook.checks":      "Checks",
        "hook.actions":     "Actions",
        "hook.notes":       "Notes",
        "hook.trigger_ph":  "Choose or enter trigger…",
        "hook.files_ph":    "Add file pattern…",
        "hook.checks_ph":   "Add check…",
        "hook.actions_ph":  "Add action…",
        "hook.notes_ph":    "Add note…",
        # Panels — Instruction
        "instr.form_title":  "Instruction / Rules",
        "instr.name":        "Name",
        "instr.apply_to":    "applyTo (glob)",
        "instr.sections":    "Sections",
        "instr.add_section": "＋ Add section…",
        # Validation
        "valid.agents_hdr":  "Agents",
        "valid.issues_hdr":  "Issues",
        "valid.all":         "🔍 All",
        "valid.run":         "↻ Refresh",
        "valid.hint":        "🔴 error  🟡 warning  🟢 OK",
        "valid.ok":          "✅  All OK — no issues found.",
        # Run panel
        "run.agent_lbl":   "Agent:",
        "run.task_lbl":    "Task / prompt:",
        "run.input_ph":    "Enter task for the agent…",
        "run.output_lbl":  "Output:",
        "run.output_ph":   "The agent's response will appear here…",
        # Export panel
        "export.agent_lbl":   "Agent:",
        "export.fmt_lbl":     "Format:",
        "export.preview_lbl": "Preview:",
        "export.all":         "All agents",
        # Settings panel
        "settings.title":           "Settings",
        "settings.section_general": "General",
        "settings.language":        "Interface language:",
        "settings.lang_pl":         "Polski",
        "settings.lang_en":         "English",
        "settings.model":           "Default LLM model:",
        "settings.workspace":       "Workspace:",
        "settings.ws_browse":       "Browse…",
        "settings.save":            "Save settings",
        "settings.saved":           "✅  Settings saved.",
        "btn.saved":                "✔ Saved",
        "settings.hint":            "Language change is immediate — labels update automatically.",
        # API Keys section
        "settings.section_api":     "API Keys",
        "settings.api_hint":        "Keys are stored locally in <code>~/.agent-manager/api_keys.env</code> and never committed to the repository.",
        "settings.api_show":        "Show",
        "settings.api_hide":        "Hide",
        # Dialogs
        "dlg.new_title":   "New {kind}",
        "dlg.new_label":   "Name:",
        "dlg.exists":      "Already exists",
        "dlg.exists_msg":  "{kind} '{name}' already exists.",
        "dlg.delete":      "Delete",
        "dlg.delete_q":    "Delete '{name}'?",
        "dlg.no_select":   "Nothing selected",
        "dlg.no_select_m": "Select an item from the list.",
        # About
        "about.title": "About",
        "about.body": (
            "<h3>Agent Manager <small style='color:#666'>v{ver}</small></h3>"
            "<p><b>What problem does it solve?</b><br>"
            "Managing AI agents in a project quickly becomes messy — "
            "dozens of prompts, skills, hooks and rules scattered in files with no structure. "
            "Agent Manager provides a graphical interface for defining agents, assigning "
            "procedures (skills) and automatic actions (hooks) to them, validating consistency "
            "and running them directly from the app — everything saved as Markdown files "
            "in <code>.github/</code>, readable by GitHub Copilot.</p>"
            "<p><b>Supported models:</b> OpenAI, Anthropic, Google Gemini "
            "(and any other supported by litellm).</p>"
            "<p><b>Repository:</b> "
            "<a href='https://github.com/Korey90/agent-manager'>"
            "github.com/Korey90/agent-manager</a></p>"
        ),
    },
}

# ─────────────────────────────────────────────────────────────────────────────

_lang: str = "pl"


class _I18nSignals(QObject):
    changed = pyqtSignal()


_signals = _I18nSignals()


def lang_signals() -> _I18nSignals:
    return _signals


def set_lang(lang: str) -> None:
    global _lang
    if lang in _STRINGS:
        _lang = lang
        _signals.changed.emit()


def get_lang() -> str:
    return _lang


def tr(key: str, **kwargs) -> str:
    text = _STRINGS.get(_lang, _STRINGS["pl"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
