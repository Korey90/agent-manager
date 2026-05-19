"""Panels — each tab of the main window: list (left) + detail form (right)."""
from __future__ import annotations

from typing import Any

from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from gui.widgets import CodeEditor, ListEditor


# ── helpers ───────────────────────────────────────────────────────────────────

def _sep() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setFrameShadow(QFrame.Shadow.Sunken)
    return sep


def _label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-weight: bold; color: #555;")
    return lbl


def _info_banner(text: str, color: str = "#E8F4FD", border: str = "#6CB4E4") -> QLabel:
    """Styled info/description banner for the top of a form."""
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setTextFormat(Qt.TextFormat.RichText)
    lbl.setStyleSheet(
        f"background:{color}; border-left:4px solid {border};"
        " border-radius:3px; padding:6px 10px;"
        " color:#333; font-size:11px; margin-bottom:4px;"
    )
    return lbl


# ── Base Panel ────────────────────────────────────────────────────────────────

class BasePanel(QWidget):
    """
    Abstract base: left = item list + New/Delete buttons,
    right = scroll-area with a detail form.
    """

    _ITEM_KIND = "item"   # overridden by subclasses

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_id: str | None = None
        self._build_layout()
        self.refresh()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── left: list ──────────────────────────────────────────────────────
        left = QWidget()
        left.setMinimumWidth(200)
        left.setMaximumWidth(300)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(4, 4, 4, 4)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_select)
        lv.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("＋ Nowy")
        self.btn_del = QPushButton("✕ Usuń")
        self.btn_new.clicked.connect(self._on_new)
        self.btn_del.clicked.connect(self._on_delete)
        btn_row.addWidget(self.btn_new)
        btn_row.addWidget(self.btn_del)
        lv.addLayout(btn_row)

        splitter.addWidget(left)

        # ── right: scrollable form ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll = scroll

        form_container = QWidget()
        self._form_container = form_container
        self._form_layout = QVBoxLayout(form_container)
        self._form_layout.setContentsMargins(12, 12, 12, 12)
        self._form_layout.setSpacing(8)

        self._build_form(self._form_layout)

        save_row = QHBoxLayout()
        self.btn_save = QPushButton("💾  Zapisz")
        self.btn_save.setFixedHeight(32)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#0063B1; color:white; border-radius:4px; padding:4px 20px; }"
            "QPushButton:hover { background:#0078D4; }"
        )
        self.btn_save.clicked.connect(self._on_save)
        save_row.addStretch()
        save_row.addWidget(self.btn_save)
        self._form_layout.addLayout(save_row)
        self._form_layout.addStretch()

        scroll.setWidget(form_container)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter)

    # ── abstract hooks ────────────────────────────────────────────────────────

    def _build_form(self, layout: QVBoxLayout) -> None:
        """Subclasses add their form fields here."""
        raise NotImplementedError

    def _load_form(self, item: Any) -> None:
        """Populate form fields from item."""
        raise NotImplementedError

    def _collect_form(self) -> dict[str, Any]:
        """Collect form values into a dict for model update."""
        raise NotImplementedError

    def _get_store(self):
        from gui.state import get_registry
        raise NotImplementedError

    def _new_item(self, name: str) -> Any:
        raise NotImplementedError

    # ── list management ───────────────────────────────────────────────────────

    def refresh(self) -> None:
        prev = self._current_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        store = self._get_store()
        for item in store.list():
            self.list_widget.addItem(item.name)
            self.list_widget.item(self.list_widget.count() - 1).setData(Qt.ItemDataRole.UserRole, item.id)
        self.list_widget.blockSignals(False)
        # Reselect previous item if still exists
        if prev:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == prev:
                    self.list_widget.setCurrentRow(i)
                    return
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_select(self, row: int) -> None:
        if row < 0:
            self._current_id = None
            return
        item_id = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
        self._current_id = item_id
        store = self._get_store()
        item = store.get(item_id)
        if item:
            self._load_form(item)

    def _on_new(self) -> None:
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, f"Nowy {self._ITEM_KIND}", "Nazwa:")
        if not ok or not name.strip():
            return
        store = self._get_store()
        from storage.markdown_utils import to_slug
        slug = to_slug(name.strip())
        if store.get(slug):
            QMessageBox.warning(self, "Już istnieje", f"{self._ITEM_KIND.title()} '{name}' już istnieje.")
            return
        item = self._new_item(name.strip())
        store.save(item)
        self.refresh()
        # Select the new item
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == item.id:
                self.list_widget.setCurrentRow(i)
                break

    def _on_delete(self) -> None:
        if not self._current_id:
            return
        store = self._get_store()
        item = store.get(self._current_id)
        if not item:
            return
        reply = QMessageBox.question(
            self, "Usuń", f"Usunąć '{item.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            store.delete(self._current_id)
            self._current_id = None
            self.refresh()

    def _on_save(self) -> None:
        if not self._current_id:
            QMessageBox.information(self, "Brak wyboru", "Wybierz element z listy.")
            return
        try:
            store = self._get_store()
            item = store.get(self._current_id)
            if not item:
                return
            data = self._collect_form()
            for key, val in data.items():
                setattr(item, key, val)
            item.touch()
            store.save(item)
            self.refresh()
        except Exception as exc:
            import traceback
            QMessageBox.critical(self, "Błąd zapisu",
                                  f"Nie udało się zapisać:\n\n{traceback.format_exc()}")

    def select_by_id(self, item_id: str) -> None:
        """Select an item by id in the list and briefly flash the form border."""
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == item_id:
                self.list_widget.setCurrentRow(i)
                self._flash_form()
                return

    def _flash_form(self) -> None:
        """Show a brief orange border on the form scroll area, then clear it."""
        self._scroll.setStyleSheet(
            "QScrollArea { border:2px solid #E67E22; border-radius:4px; }"
        )
        QTimer.singleShot(1400, lambda: self._scroll.setStyleSheet(
            "QScrollArea { border:none; }"
        ))


# ── Agent Panel ───────────────────────────────────────────────────────────────

class AgentPanel(BasePanel):
    _ITEM_KIND = "agent"

    def _get_store(self):
        from gui.state import get_registry
        return get_registry().agents

    def _new_item(self, name: str):
        from core.agent import Agent
        from storage.markdown_utils import to_slug
        return Agent(id=to_slug(name), name=name)

    _MODELS = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo",
        "claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-3-5",
        "gemini/gemini-2.0-flash", "ollama/llama3",
    ]

    def _build_form(self, layout: QVBoxLayout) -> None:
        layout.addWidget(_info_banner(
            "<b>Agent</b> to samodzielna jednostka AI ze zdefiniowaną rolą, modelem LLM i zestawem skilli. "
            "Każdy agent jest zapisywany jako plik <code>.github/agents/&lt;id&gt;.md</code>. "
            "Przypisz skille (checkboxy poniżej), by agent wiedział, z jakich narzędzi korzystać."
        ))
        layout.addWidget(_label("Agent"))
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_role = QLineEdit()
        self.f_desc = QPlainTextEdit(); self.f_desc.setMaximumHeight(60)
        self.f_model = QComboBox(); self.f_model.setEditable(True)
        self.f_model.addItems(self._MODELS)
        fl.addRow("Nazwa:", self.f_name)
        fl.addRow("Rola:", self.f_role)
        fl.addRow("Opis:", self.f_desc)
        fl.addRow("Model LLM:", self.f_model)
        layout.addLayout(fl)

        layout.addWidget(_label("Specjalizacja"))
        self.f_spec = ListEditor("Dodaj specjalizację…")
        layout.addWidget(self.f_spec)

        layout.addWidget(_label("Obowiązki"))
        self.f_resp = ListEditor("Dodaj obowiązek…")
        layout.addWidget(self.f_resp)

        layout.addWidget(_label("Twarde zasady (Hard Rules)"))
        self.f_rules = ListEditor("Dodaj zasadę…")
        layout.addWidget(self.f_rules)

        layout.addWidget(_label("Preferowane wzorce"))
        self.f_patterns = ListEditor("Dodaj wzorzec…")
        layout.addWidget(self.f_patterns)

        layout.addWidget(_label("Notatki"))
        self.f_notes = ListEditor("Dodaj notatkę…")
        layout.addWidget(self.f_notes)

        layout.addWidget(_label("Skille agenta"))
        self.f_skills = QListWidget()
        self.f_skills.setMinimumHeight(150)
        self.f_skills.setToolTip("Zaznacz skille używane przez tego agenta")
        layout.addWidget(self.f_skills)

        layout.addWidget(_label("Hooki agenta"))
        self.f_hooks = QListWidget()
        self.f_hooks.setMinimumHeight(120)
        self.f_hooks.setToolTip("Zaznacz hooki przypisane do tego agenta")
        layout.addWidget(self.f_hooks)

        layout.addWidget(_label("Instrukcje agenta"))
        self.f_instructions = QListWidget()
        self.f_instructions.setMinimumHeight(100)
        self.f_instructions.setToolTip("Zaznacz instrukcje (reguły) przypisane do tego agenta")
        layout.addWidget(self.f_instructions)

    def _populate_skills(self, selected_ids: list[str]) -> None:
        from gui.state import get_registry
        self.f_skills.clear()
        try:
            skills = get_registry().skills.list()
        except Exception:
            return
        for skill in sorted(skills, key=lambda s: s.name):
            item = QListWidgetItem(skill.name)
            item.setData(Qt.ItemDataRole.UserRole, skill.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if skill.id in selected_ids
                else Qt.CheckState.Unchecked
            )
            self.f_skills.addItem(item)

    def _populate_hooks(self, selected_ids: list[str]) -> None:
        from gui.state import get_registry
        self.f_hooks.clear()
        try:
            hooks = get_registry().hooks.list()
        except Exception:
            return
        for hook in sorted(hooks, key=lambda h: h.name):
            item = QListWidgetItem(hook.name)
            item.setData(Qt.ItemDataRole.UserRole, hook.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if hook.id in selected_ids
                else Qt.CheckState.Unchecked
            )
            self.f_hooks.addItem(item)

    def _populate_instructions(self, selected_ids: list[str]) -> None:
        from gui.state import get_registry
        self.f_instructions.clear()
        try:
            instructions = get_registry().instructions.list()
        except Exception:
            return
        for instr in sorted(instructions, key=lambda i: i.name):
            item = QListWidgetItem(instr.name)
            item.setData(Qt.ItemDataRole.UserRole, instr.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if instr.id in selected_ids
                else Qt.CheckState.Unchecked
            )
            self.f_instructions.addItem(item)

    def _load_form(self, item) -> None:
        self.f_name.setText(item.name)
        self.f_role.setText(item.role or "")
        self.f_desc.setPlainText(item.description or "")
        idx = self.f_model.findText(item.model or "gpt-4o")
        if idx >= 0:
            self.f_model.setCurrentIndex(idx)
        else:
            self.f_model.setCurrentText(item.model or "gpt-4o")
        self.f_spec.set_items(item.specialization)
        self.f_resp.set_items(item.responsibilities)
        self.f_rules.set_items(item.hard_rules)
        self.f_patterns.set_items(item.preferred_patterns)
        self.f_notes.set_items(item.notes)
        self._populate_skills(item.skill_ids)
        self._populate_hooks(item.hook_ids)
        self._populate_instructions(item.instruction_ids)

    def _collect_form(self) -> dict:
        skill_ids = []
        for i in range(self.f_skills.count()):
            it = self.f_skills.item(i)
            if it.checkState() == Qt.CheckState.Checked:
                skill_ids.append(it.data(Qt.ItemDataRole.UserRole))
        hook_ids = []
        for i in range(self.f_hooks.count()):
            it = self.f_hooks.item(i)
            if it.checkState() == Qt.CheckState.Checked:
                hook_ids.append(it.data(Qt.ItemDataRole.UserRole))
        instruction_ids = []
        for i in range(self.f_instructions.count()):
            it = self.f_instructions.item(i)
            if it.checkState() == Qt.CheckState.Checked:
                instruction_ids.append(it.data(Qt.ItemDataRole.UserRole))
        return {
            "role": self.f_role.text().strip(),
            "description": self.f_desc.toPlainText().strip(),
            "model": self.f_model.currentText().strip() or "gpt-4o",
            "specialization": self.f_spec.get_items(),
            "responsibilities": self.f_resp.get_items(),
            "hard_rules": self.f_rules.get_items(),
            "preferred_patterns": self.f_patterns.get_items(),
            "notes": self.f_notes.get_items(),
            "skill_ids": skill_ids,
            "hook_ids": hook_ids,
            "instruction_ids": instruction_ids,
        }


# ── Skill Panel ───────────────────────────────────────────────────────────────

class SkillPanel(BasePanel):
    _ITEM_KIND = "skill"

    def _get_store(self):
        from gui.state import get_registry
        return get_registry().skills

    def _new_item(self, name: str):
        from core.skill import Skill
        from storage.markdown_utils import to_slug
        return Skill(id=to_slug(name), name=name)

    def _build_form(self, layout: QVBoxLayout) -> None:
        layout.addWidget(_info_banner(
            "<b>Skill</b> to workflow kroków z jasnymi <i>exit criteria</i> (wg Agent Skills). "
            "Dodaj fazę SDLC, kroki (Steps), warunek ukończenia (Exit Criteria), zasady i "
            "<i>anti-rationalizations</i> — rebuttals do wymówek, które agent może podać żeby pominąć workflow. "
            "Plik: <code>.github/skills/&lt;id&gt;.md</code>.",
            color="#EBF5EB", border="#5CB85C"
        ))
        layout.addWidget(_label("Skill"))
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_desc = QPlainTextEdit(); self.f_desc.setMaximumHeight(60)
        self.f_phase = QComboBox()
        self.f_phase.addItems([
            "general", "define (spec)", "plan", "build",
            "verify (test)", "review", "ship",
        ])
        self.f_phase.setToolTip("Faza SDLC wg metodologii Agent Skills (Addy Osmani)")
        self.f_when = QComboBox(); self.f_when.setEditable(True)
        self.f_when.setPlaceholderText("Wybierz lub opisz sytuację…")
        self.f_when.addItems([
            "user wants to create a new complete project from scratch",
            "user asks to create a new feature",
            "user asks to refactor existing code",
            "user wants to generate tests",
            "user asks to fix a bug",
            "user wants to create a database migration",
            "user asks to create a new API endpoint",
            "user wants to create a UI component",
            "user asks to review or analyze code",
            "user asks to write documentation",
            "user wants to integrate a third-party service",
            "user asks to optimize performance",
            "user asks to add authentication or authorization",
            "user wants to deploy or configure infrastructure",
            "user asks to create a report or export",
        ])
        self.f_when.setCurrentIndex(-1)
        fl.addRow("Nazwa:", self.f_name)
        fl.addRow("Opis:", self.f_desc)
        fl.addRow("Faza SDLC:", self.f_phase)
        fl.addRow("Kiedy użyć:", self.f_when)
        layout.addLayout(fl)

        layout.addWidget(_label("Kroki (Steps)"))
        self.f_steps = ListEditor("Dodaj krok…")
        layout.addWidget(self.f_steps)

        layout.addWidget(_info_banner(
            "⬛ <b>Exit criteria</b> — opisz konkretny, weryfikowalny warunek ukończenia zadania. "
            "Np. <i>\"testy przechodzą, build jest czysty, reviewer zaakceptował\"</i>. "
            "Bez tego agent nie wie kiedy zadanie jest naprawdę skończone.",
            color="#F0F9FF", border="#0EA5E9"
        ))
        self.f_exit = QPlainTextEdit()
        self.f_exit.setMaximumHeight(65)
        self.f_exit.setPlaceholderText("np. All tests pass, build is clean, no linting errors, reviewer approved…")
        layout.addWidget(self.f_exit)

        layout.addWidget(_label("Zasady (Rules)"))
        self.f_rules = ListEditor("Dodaj zasadę…")
        layout.addWidget(self.f_rules)

        layout.addWidget(_info_banner(
            "🔄 <b>Anti-rationalizations</b> — rebuttals do wymówek agenta. "
            "Format: <i>wymówka | odpowiedź</i>, np. "
            "<i>\"This is too simple for a spec | Acceptance criteria still apply.\"</i>",
            color="#FFF7ED", border="#F97316"
        ))
        self.f_anti = ListEditor("Dodaj: wymówka | obalenie…")
        layout.addWidget(self.f_anti)

        fl2 = QFormLayout()
        fl2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_lang = QComboBox(); self.f_lang.setEditable(True)
        self.f_lang.setPlaceholderText("php / python / ts…")
        self.f_lang.addItems(["php", "python", "typescript", "javascript", "bash", "sql", "html", "css", "json", "yaml", "markdown"])
        self.f_lang.setCurrentIndex(-1)
        self.f_out = QComboBox(); self.f_out.setEditable(True)
        self.f_out.setPlaceholderText("Wybierz lub wpisz format…")
        self.f_out.addItems([
            "markdown", "json", "yaml", "xml",
            "plain text", "HTML", "PHP class", "TypeScript interface",
            "Python class", "SQL migration", "Bash script",
            "React component", "Vue component",
            "numbered list", "bullet list", "table",
        ])
        self.f_out.setCurrentIndex(-1)
        fl2.addRow("Język szablonu:", self.f_lang)
        fl2.addRow("Format wyjścia:", self.f_out)
        layout.addLayout(fl2)

        layout.addWidget(_label("Szablon kodu (Template)"))
        self.f_tmpl = CodeEditor()
        layout.addWidget(self.f_tmpl)

    def _load_form(self, item) -> None:
        self.f_name.setText(item.name)
        self.f_desc.setPlainText(item.description or "")
        phase_raw = getattr(item.phase, "value", str(item.phase)) if getattr(item, "phase", None) else "general"
        phase_map = {
            "general": "general", "define": "define (spec)", "plan": "plan",
            "build": "build", "verify": "verify (test)", "review": "review", "ship": "ship",
        }
        self.f_phase.setCurrentText(phase_map.get(phase_raw, "general"))
        idx = self.f_when.findText(item.when_to_use or "")
        if idx >= 0:
            self.f_when.setCurrentIndex(idx)
        else:
            self.f_when.setCurrentText(item.when_to_use or "")
        self.f_steps.set_items(item.steps)
        self.f_exit.setPlainText(getattr(item, "exit_criteria", "") or "")
        self.f_rules.set_items(item.rules)
        self.f_anti.set_items(getattr(item, "anti_rationalizations", []))
        self.f_lang.setCurrentText(item.template_language or "")
        idx = self.f_out.findText(item.output_format or "")
        if idx >= 0:
            self.f_out.setCurrentIndex(idx)
        else:
            self.f_out.setCurrentText(item.output_format or "")
        self.f_tmpl.setPlainText(item.template or "")

    def _collect_form(self) -> dict:
        from core.skill import SkillPhase
        phase_display = self.f_phase.currentText()
        phase_reverse = {
            "general": "general", "define (spec)": "define", "plan": "plan",
            "build": "build", "verify (test)": "verify", "review": "review", "ship": "ship",
        }
        phase_val = phase_reverse.get(phase_display, "general")
        return {
            "description": self.f_desc.toPlainText().strip(),
            "phase": SkillPhase(phase_val),
            "when_to_use": self.f_when.currentText().strip(),
            "steps": self.f_steps.get_items(),
            "exit_criteria": self.f_exit.toPlainText().strip(),
            "rules": self.f_rules.get_items(),
            "anti_rationalizations": self.f_anti.get_items(),
            "template_language": self.f_lang.currentText().strip(),
            "output_format": self.f_out.currentText().strip(),
            "template": self.f_tmpl.toPlainText(),
        }


# ── Hook Panel ────────────────────────────────────────────────────────────────

class HookPanel(BasePanel):
    _ITEM_KIND = "hook"

    def _get_store(self):
        from gui.state import get_registry
        return get_registry().hooks

    def _new_item(self, name: str):
        from core.hook import Hook
        from storage.markdown_utils import to_slug
        return Hook(id=to_slug(name), name=name)

    _TRIGGERS = [
        "on-save", "pre-commit", "post-commit", "pre-push", "post-push",
        "post-generation", "after-feature-completion", "on-error", "manual",
    ]
    _EVENTS = ["pre_run", "post_run", "on_error", "on_skill_call", "on_response"]
    _TYPES  = ["python", "builtin"]

    def _build_form(self, layout: QVBoxLayout) -> None:
        layout.addWidget(_info_banner(
            "<b>Hook</b> to akcja automatycznie wyzwalana przez zdarzenie w cyklu życia agenta. "
            "Ustaw <i>wyzwalacz</i> (np. pre-commit, on-save), <i>zdarzenie</i> (pre_run / post_run / on_error) "
            "i <i>typ</i> (python = skrypt, builtin = wbudowana funkcja). "
            "Pliki hooków: <code>.github/hooks/&lt;id&gt;.md</code>.",
            color="#FFF8E1", border="#F0AD4E"
        ))
        layout.addWidget(_label("Hook"))
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_desc = QPlainTextEdit(); self.f_desc.setMaximumHeight(60)

        self.f_trigger = QComboBox(); self.f_trigger.setEditable(True)
        self.f_trigger.addItems(self._TRIGGERS)
        self.f_trigger.setCurrentIndex(-1)
        self.f_trigger.lineEdit().setPlaceholderText("Wybierz lub wpisz wyzwalacz…")

        self.f_failure = QLineEdit()

        self.f_event = QComboBox()
        self.f_event.addItems(self._EVENTS)
        self.f_type = QComboBox()
        self.f_type.addItems(self._TYPES)
        self.f_priority = QSpinBox()
        self.f_priority.setRange(0, 9999); self.f_priority.setValue(100)

        fl.addRow("Nazwa:", self.f_name)
        fl.addRow("Opis:", self.f_desc)
        fl.addRow("Wyzwalacz:", self.f_trigger)
        fl.addRow("Przy błędzie:", self.f_failure)
        fl.addRow("Zdarzenie (event):", self.f_event)
        fl.addRow("Typ:", self.f_type)
        fl.addRow("Priorytet:", self.f_priority)
        layout.addLayout(fl)

        layout.addWidget(_label("Pliki (For files in)"))
        self.f_files = ListEditor("Dodaj wzorzec pliku…")
        layout.addWidget(self.f_files)

        layout.addWidget(_label("Sprawdzenia (Checks)"))
        self.f_checks = ListEditor("Dodaj sprawdzenie…")
        layout.addWidget(self.f_checks)

        layout.addWidget(_label("Akcje (Actions)"))
        self.f_actions = ListEditor("Dodaj akcję…")
        layout.addWidget(self.f_actions)

        layout.addWidget(_label("Notatki"))
        self.f_notes = ListEditor("Dodaj notatkę…")
        layout.addWidget(self.f_notes)

    def _load_form(self, item) -> None:
        self.f_name.setText(item.name)
        self.f_desc.setPlainText(item.description or "")
        trigger = item.trigger or ""
        idx = self.f_trigger.findText(trigger)
        if idx >= 0:
            self.f_trigger.setCurrentIndex(idx)
        else:
            self.f_trigger.setCurrentText(trigger)
        self.f_failure.setText(item.on_failure or "")
        ev = item.event.value if hasattr(item.event, 'value') else str(item.event)
        self.f_event.setCurrentText(ev)
        tp = item.type.value if hasattr(item.type, 'value') else str(item.type)
        self.f_type.setCurrentText(tp)
        self.f_priority.setValue(item.priority or 100)
        self.f_files.set_items(item.for_files)
        self.f_checks.set_items(item.checks)
        self.f_actions.set_items(item.actions)
        self.f_notes.set_items(item.notes)

    def _collect_form(self) -> dict:
        return {
            "description": self.f_desc.toPlainText().strip(),
            "trigger": self.f_trigger.currentText().strip(),
            "on_failure": self.f_failure.text().strip(),
            "event": self.f_event.currentText(),
            "type": self.f_type.currentText(),
            "priority": self.f_priority.value(),
            "for_files": self.f_files.get_items(),
            "checks": self.f_checks.get_items(),
            "actions": self.f_actions.get_items(),
            "notes": self.f_notes.get_items(),
        }


# ── Instruction helpers ────────────────────────────────────────────────────────
import re as _re


def _parse_apply_to(raw: str) -> str:
    m = _re.match(r'^---\n(.*?)---\n', raw, _re.DOTALL)
    if m:
        am = _re.search(r'^applyTo:\s*["\']?(.*?)["\']?\s*$', m.group(1), _re.MULTILINE)
        if am:
            return am.group(1).strip()
    return ""


def _strip_frontmatter(raw: str) -> str:
    return _re.sub(r'^---\n.*?---\n', '', raw, flags=_re.DOTALL)


def _set_apply_to(body: str, apply_to: str) -> str:
    if apply_to:
        return f'---\napplyTo: "{apply_to}"\n---\n{body}'
    return body


# ── Instruction Panel ─────────────────────────────────────────────────────────

class InstructionPanel(BasePanel):
    _ITEM_KIND = "instruction"

    _APPLY_PRESETS = [
        "**",
        "**/*.ts", "**/*.tsx",
        "**/*.py",
        "**/*.php",
        "**/*.js", "**/*.jsx",
        "**/*.vue",
        "src/**", "app/**",
        "tests/**", "resources/**",
        "**/*.md",
    ]

    _SECTION_TEMPLATES = [
        ("Wytyczne kodowania",    "## Coding Guidelines\n\n- \n"),
        ("Zakazane wzorce",       "## Forbidden Patterns\n\n- \n"),
        ("Reguły (Rules)",        "## Rules\n\n1. \n"),
        ("Przykłady",             "## Examples\n\n```\n\n```\n"),
        ("Kontekst projektu",     "## Project Context\n\n"),
        ("Stack technologiczny",  "## Tech Stack\n\n- \n"),
        ("Struktura folderów",    "## Folder Structure\n\n```\n\n```\n"),
        ("Konwencje nazewnictwa", "## Naming Conventions\n\n- \n"),
        ("Bezpieczeństwo",        "## Security\n\n- \n"),
        ("Testowanie",            "## Testing\n\n- \n"),
    ]

    def _get_store(self):
        from gui.state import get_registry
        return get_registry().instructions

    def _new_item(self, name: str):
        from core.instruction import Instruction
        from storage.markdown_utils import to_slug
        return Instruction(id=to_slug(name), name=name, raw_content=f"# {name}\n\n")

    # Override to avoid QScrollArea — editor must fill vertical space freely
    def _build_layout(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # left: list (mirrors BasePanel)
        left = QWidget()
        left.setMinimumWidth(200); left.setMaximumWidth(300)
        lv = QVBoxLayout(left); lv.setContentsMargins(4, 4, 4, 4)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_select)
        lv.addWidget(self.list_widget)
        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("＋ Nowy")
        self.btn_del = QPushButton("✕ Usuń")
        self.btn_new.clicked.connect(self._on_new)
        self.btn_del.clicked.connect(self._on_delete)
        btn_row.addWidget(self.btn_new); btn_row.addWidget(self.btn_del)
        lv.addLayout(btn_row)
        splitter.addWidget(left)

        # right: editor-first, no outer scroll area
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(12, 12, 12, 12); rv.setSpacing(6)
        self._build_form(rv)
        save_row = QHBoxLayout()
        self.btn_save = QPushButton("💾  Zapisz")
        self.btn_save.setFixedHeight(32)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#0063B1; color:white;"
            " border-radius:4px; padding:4px 20px; }"
            "QPushButton:hover { background:#0078D4; }"
        )
        self.btn_save.clicked.connect(self._on_save)
        save_row.addStretch(); save_row.addWidget(self.btn_save)
        rv.addLayout(save_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter)

    def _build_form(self, layout: QVBoxLayout) -> None:
        layout.addWidget(_info_banner(
            "<b>Instruction</b> to zestaw reguł i wytycznych dla Copilota — np. konwencje kodowania, "
            "zakazane wzorce lub kontekst projektu. Pole <i>applyTo</i> (glob) decyduje, "
            "do jakich plików instrukcja jest dołączana (np. <code>**/*.ts</code> tylko dla TypeScriptu). "
            "Plik zapisywany w <code>.github/instructions/&lt;id&gt;.md</code> z YAML frontmatter.",
            color="#F5E6FF", border="#9B59B6"
        ))
        layout.addWidget(_label("Instruction / Rules"))
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_apply = QComboBox(); self.f_apply.setEditable(True)
        self.f_apply.setPlaceholderText("np. **/*.ts  lub  ** (puste = brak applyTo)")
        self.f_apply.addItems([""] + self._APPLY_PRESETS)
        self.f_apply.setCurrentIndex(0)
        fl.addRow("Nazwa:", self.f_name)
        fl.addRow("applyTo:", self.f_apply)
        layout.addLayout(fl)
        layout.addWidget(_sep())

        # Inner splitter: sections navigator | editor
        inner = QSplitter(Qt.Orientation.Horizontal)

        nav = QWidget(); nav.setMaximumWidth(210)
        nv = QVBoxLayout(nav); nv.setContentsMargins(0, 0, 4, 0); nv.setSpacing(4)
        nv.addWidget(_label("Sekcje"))
        self.f_sections = QListWidget()
        nv.addWidget(self.f_sections, 1)
        self.btn_add_sec = QPushButton("＋ Dodaj sekcję…")
        self.btn_add_sec.clicked.connect(self._show_add_section_menu)
        nv.addWidget(self.btn_add_sec)
        inner.addWidget(nav)

        self.f_content = CodeEditor()
        self.f_content.setMinimumHeight(200)
        inner.addWidget(self.f_content)
        inner.setStretchFactor(0, 1)
        inner.setStretchFactor(1, 4)
        layout.addWidget(inner, 1)  # stretch=1: fills remaining vertical space

        # Debounced section refresh
        self._sec_timer = QTimer()
        self._sec_timer.setSingleShot(True)
        self._sec_timer.setInterval(400)
        self._sec_timer.timeout.connect(self._refresh_sections)
        self.f_content.textChanged.connect(self._sec_timer.start)
        self.f_sections.currentRowChanged.connect(self._on_section_click)

    # ── section navigator ─────────────────────────────────────────────────────

    def _refresh_sections(self) -> None:
        import re
        text = self.f_content.toPlainText()
        self.f_sections.blockSignals(True)
        self.f_sections.clear()
        for i, line in enumerate(text.splitlines()):
            m = re.match(r'^(#{1,6})\s+(.*)', line)
            if m:
                depth = len(m.group(1)) - 1
                item = QListWidgetItem("  " * depth + m.group(2))
                item.setData(Qt.ItemDataRole.UserRole, i)
                self.f_sections.addItem(item)
        self.f_sections.blockSignals(False)

    def _on_section_click(self, row: int) -> None:
        if row < 0:
            return
        line_num = self.f_sections.item(row).data(Qt.ItemDataRole.UserRole)
        block = self.f_content.document().findBlockByLineNumber(line_num)
        if block.isValid():
            cursor = self.f_content.textCursor()
            cursor.setPosition(block.position())
            self.f_content.setTextCursor(cursor)
            self.f_content.ensureCursorVisible()
            self.f_content.setFocus()

    def _show_add_section_menu(self) -> None:
        from PyQt6.QtCore import QPoint
        menu = QMenu(self)
        for name, tmpl in self._SECTION_TEMPLATES:
            menu.addAction(name, lambda t=tmpl: self._append_section(t))
        btn = self.btn_add_sec
        menu.exec(btn.mapToGlobal(QPoint(0, btn.height())))

    def _append_section(self, template: str) -> None:
        from PyQt6.QtGui import QTextCursor
        cursor = self.f_content.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text = self.f_content.toPlainText()
        sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        cursor.insertText(sep + template)
        self.f_content.setTextCursor(cursor)
        self.f_content.ensureCursorVisible()

    # ── form I/O ──────────────────────────────────────────────────────────────

    def _load_form(self, item) -> None:
        self.f_name.setText(item.name)
        raw = item.raw_content or ""
        apply_to = _parse_apply_to(raw)
        body = _strip_frontmatter(raw)
        idx = self.f_apply.findText(apply_to)
        if idx >= 0:
            self.f_apply.setCurrentIndex(idx)
        else:
            self.f_apply.setCurrentText(apply_to)
        self.f_content.setPlainText(body)
        self._refresh_sections()

    def _collect_form(self) -> dict:
        apply_to = self.f_apply.currentText().strip()
        raw = _set_apply_to(self.f_content.toPlainText(), apply_to)
        return {
            "raw_content": raw,
            "metadata": {"applyTo": apply_to} if apply_to else {},
        }


# ── Issue Row widget ─────────────────────────────────────────────────────────

class _IssueRow(QWidget):
    """One row in the validation list: icon + message + optional jump button."""

    def __init__(
        self,
        icon: str,
        msg: str,
        color: str,
        kind: str | None,
        item_id: str | None,
        on_nav,
    ) -> None:
        super().__init__()
        h = QHBoxLayout(self)
        h.setContentsMargins(4, 1, 4, 1)
        h.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedWidth(22)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(icon_lbl)

        msg_lbl = QLabel(msg)
        msg_lbl.setStyleSheet(f"color:{color};")
        h.addWidget(msg_lbl, stretch=1)

        if kind and item_id:
            btn = QPushButton("\u21d7")
            btn.setFixedSize(22, 22)
            btn.setToolTip("Przejd\u017a do tego elementu")
            btn.setStyleSheet(
                "QPushButton { border:1px solid #C8C8C8; border-radius:3px;"
                " background:#F5F5F5; color:#555; font-size:11px; }"
                "QPushButton:hover { background:#D6EAFF; border-color:#5B9BD5; color:#003; }"
            )
            btn.clicked.connect(
                lambda checked=False, k=kind, i=item_id: on_nav(k, i)
            )
            h.addWidget(btn)


# ── Validation Panel ──────────────────────────────────────────────────────────

class ValidationPanel(QWidget):
    """Walidacja z list\u0105 agent\u00f3w po lewej i widokiem problem\u00f3w po prawej."""

    navigate_to = pyqtSignal(str, str)  # (kind: "agent"|"skill"|"hook", item_id)

    _COLORS = {"error": "#C0392B", "warning": "#E67E22", "info": "#2980B9"}
    _ICONS  = {"error": "\u274c", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}
    _DOT    = {"error": "\U0001f534", "warning": "\U0001f7e1", "info": "\U0001f535", "ok": "\U0001f7e2"}

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._refresh_agents()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        # ── compact top bar ───────────────────────────────────────────────────
        top = QHBoxLayout()
        self.btn_refresh = QPushButton("\u21bb  Od\u015bwie\u017c")
        self.btn_refresh.setFixedHeight(28)
        self.btn_refresh.setFixedWidth(110)
        self.btn_refresh.clicked.connect(self._refresh_agents)
        top.addWidget(self.btn_refresh)

        hint = QLabel(
            "Wybierz agenta, by zobaczy\u0107 jego problemy. "
            "\U0001f534\u00a0b\u0142\u0105d\u2003\U0001f7e1\u00a0ostrze\u017cenie\u2003\U0001f7e2\u00a0OK"
        )
        hint.setStyleSheet("color:#777; font-size:11px;")
        hint.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top.addSpacing(8)
        top.addWidget(hint)
        top.addStretch()

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color:#444; font-size:11px; font-weight:500;")
        top.addWidget(self.stats_label)
        root.addLayout(top)

        root.addWidget(_sep())

        # ── splitter: agents | issues ─────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # left: agent list
        left = QWidget()
        left.setMinimumWidth(160)
        left.setMaximumWidth(260)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 2, 4, 0)
        lv.setSpacing(2)
        agent_hdr = QLabel("<b>Agenci</b>")
        agent_hdr.setStyleSheet("font-size:12px; padding:2px 0;")
        lv.addWidget(agent_hdr)
        self.agent_list = QListWidget()
        self.agent_list.setSpacing(1)
        self.agent_list.setStyleSheet(
            "QListWidget { border:1px solid #DDD; border-radius:3px; }"
            "QListWidget::item { padding:3px 4px; }"
            "QListWidget::item:selected { background:#D0E8FF; color:#000; }"
        )
        self.agent_list.currentRowChanged.connect(self._on_agent_selected)
        lv.addWidget(self.agent_list)
        splitter.addWidget(left)

        # right: issues
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(4, 2, 0, 0)
        rv.setSpacing(2)
        issues_hdr = QLabel("<b>Problemy</b>")
        issues_hdr.setStyleSheet("font-size:12px; padding:2px 0;")
        rv.addWidget(issues_hdr)
        self.issue_list = QListWidget()
        self.issue_list.setAlternatingRowColors(True)
        self.issue_list.setSpacing(2)
        self.issue_list.setStyleSheet(
            "QListWidget { border:1px solid #DDD; border-radius:3px; font-size:12px; }"
            "QListWidget::item { padding:4px 6px; }"
        )
        rv.addWidget(self.issue_list)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, stretch=1)

    # ── agent list ────────────────────────────────────────────────────────────

    def _refresh_agents(self) -> None:
        """Reload agent list, annotate each with worst-severity dot, keep selection."""
        try:
            from gui.state import get_registry
            agents = get_registry().agents.list()
        except Exception:
            agents = []

        prev_id = None
        cur = self.agent_list.currentItem()
        if cur:
            prev_id = cur.data(Qt.ItemDataRole.UserRole)

        self.agent_list.blockSignals(True)
        self.agent_list.clear()

        # "All" entry
        all_item = QListWidgetItem("\U0001f50e  Wszystkie")
        all_item.setData(Qt.ItemDataRole.UserRole, None)
        self.agent_list.addItem(all_item)

        for agent in agents:
            issues  = self._collect_issues(agent_id=agent.id)
            worst   = self._worst(issues)
            dot     = self._DOT[worst]
            item    = QListWidgetItem(f"{dot}  {agent.name}")
            item.setData(Qt.ItemDataRole.UserRole, agent.id)
            self.agent_list.addItem(item)

        self.agent_list.blockSignals(False)

        # restore previous selection
        restored = False
        if prev_id is not None:
            for i in range(self.agent_list.count()):
                if self.agent_list.item(i).data(Qt.ItemDataRole.UserRole) == prev_id:
                    self.agent_list.setCurrentRow(i)
                    restored = True
                    break
        if not restored:
            self.agent_list.setCurrentRow(0)

    def _on_agent_selected(self, row: int) -> None:
        if row < 0:
            return
        agent_id = self.agent_list.item(row).data(Qt.ItemDataRole.UserRole)
        self._show_issues(agent_id)

    # ── checks ────────────────────────────────────────────────────────────────

    def _worst(self, issues: list) -> str:
        for sev in ("error", "warning", "info"):
            if any(issue[1] == sev for issue in issues):
                return sev
        return "ok"

    def _collect_issues(self, agent_id: str | None = None) -> list[tuple]:
        """Return list of (icon, severity, message, kind, item_id) tuples."""
        issues: list[tuple] = []
        try:
            from gui.state import get_registry
            reg    = get_registry()
            agents = [a for a in reg.agents.list()
                      if agent_id is None or a.id == agent_id]

            skill_ids: set[str] = set()
            for agent in agents:
                skill_ids.update(agent.skill_ids)
            if agent_id is None:
                skill_ids.update(s.id for s in reg.skills.list())

            for sid in skill_ids:
                skill = reg.skills.get(sid)
                if not skill:
                    continue
                if not skill.steps:
                    issues.append(("\u274c", "error",
                                   f"Skill \u201e{skill.name}\u201c: brak krok\u00f3w (Steps)",
                                   "skill", skill.id))
                if not getattr(skill, "exit_criteria", ""):
                    issues.append(("\u26a0\ufe0f", "warning",
                                   f"Skill \u201e{skill.name}\u201c: brak exit criteria",
                                   "skill", skill.id))
                if not skill.when_to_use:
                    issues.append(("\u26a0\ufe0f", "warning",
                                   f"Skill \u201e{skill.name}\u201c: brak pola \u2018When to use\u2019",
                                   "skill", skill.id))
                if not getattr(skill, "anti_rationalizations", []):
                    issues.append(("\u2139\ufe0f", "info",
                                   f"Skill \u201e{skill.name}\u201c: brak anti-rationalizations",
                                   "skill", skill.id))

            for agent in agents:
                if not agent.skill_ids:
                    issues.append(("\u26a0\ufe0f", "warning",
                                   f"Agent \u201e{agent.name}\u201c: brak przypisanych skilli",
                                   "agent", agent.id))
                if not getattr(agent, "description", "") and not getattr(agent, "role", ""):
                    issues.append(("\u26a0\ufe0f", "warning",
                                   f"Agent \u201e{agent.name}\u201c: brak opisu i roli",
                                   "agent", agent.id))
                for sid in agent.skill_ids:
                    if not reg.skills.get(sid):
                        issues.append(("\u274c", "error",
                                       f"Agent \u201e{agent.name}\u201c: skill \u2018{sid}\u2019 nie istnieje",
                                       "agent", agent.id))
                for hid in agent.hook_ids:
                    if not reg.hooks.get(hid):
                        issues.append(("\u274c", "error",
                                       f"Agent \u201e{agent.name}\u201c: hook \u2018{hid}\u2019 nie istnieje",
                                       "agent", agent.id))

            hook_ids: set[str] = set()
            for agent in agents:
                hook_ids.update(agent.hook_ids)
            if agent_id is None:
                hook_ids.update(h.id for h in reg.hooks.list())
            for hid in hook_ids:
                hook = reg.hooks.get(hid)
                if hook and not hook.checks and not hook.actions:
                    issues.append(("\u26a0\ufe0f", "warning",
                                   f"Hook \u201e{hook.name}\u201c: brak checks i actions",
                                   "hook", hook.id))

        except Exception as exc:
            issues.append(("\u274c", "error", f"B\u0142\u0105d skanowania: {exc}", None, None))

        return issues

    # ── display ───────────────────────────────────────────────────────────────

    def _show_issues(self, agent_id: str | None = None) -> None:
        self.issue_list.clear()
        issues = self._collect_issues(agent_id=agent_id)

        if not issues:
            item = QListWidgetItem("\u2705  Wszystko OK \u2014 brak problem\u00f3w.")
            item.setForeground(QColor("#27AE60"))
            self.issue_list.addItem(item)
        else:
            for icon, severity, msg, kind, item_id in issues:
                color = self._COLORS.get(severity, "#333333")
                row   = _IssueRow(icon, msg, color, kind, item_id, self.navigate_to.emit)
                li    = QListWidgetItem()
                li.setSizeHint(QSize(0, 28))
                self.issue_list.addItem(li)
                self.issue_list.setItemWidget(li, row)

        err_count  = sum(1 for issue in issues if issue[1] == "error")
        warn_count = sum(1 for issue in issues if issue[1] == "warning")
        info_count = sum(1 for issue in issues if issue[1] == "info")
        parts = []
        if err_count:  parts.append(f"{err_count} b\u0142\u0105d{'y' if err_count > 1 else ''}")
        if warn_count: parts.append(f"{warn_count} ostrze\u017ce\u0144")
        if info_count: parts.append(f"{info_count} wskaz\u00f3wek")
        self.stats_label.setText("  \u2502  ".join(parts) if parts else "\u2705 brak problem\u00f3w")

    # keep old public name working (used by main_window init flow)
    def run_checks(self) -> None:
        self._refresh_agents()
