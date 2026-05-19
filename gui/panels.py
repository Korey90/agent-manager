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
from gui.i18n import tr


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


def _fl_row(fl: QFormLayout, key: str, widget) -> QLabel:
    """Add a translated row to a QFormLayout; return the label for retranslation."""
    lbl = QLabel(tr(key) + ":")
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    fl.addRow(lbl, widget)
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
        self._form_layout.addStretch()

        scroll.setWidget(form_container)

        # Save button lives OUTSIDE the scroll so it's always visible
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(0)
        rv.addWidget(scroll)

        save_row = QHBoxLayout()
        save_row.setContentsMargins(12, 6, 12, 6)
        self.btn_save = QPushButton(tr("btn.save"))
        self.btn_save.setFixedHeight(32)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#0063B1; color:white; border-radius:4px; padding:4px 20px; }"
            "QPushButton:hover { background:#0078D4; }"
        )
        self.btn_save.clicked.connect(self._on_save)
        save_row.addStretch()
        save_row.addWidget(self.btn_save)
        rv.addLayout(save_row)

        splitter.addWidget(right)
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
        name, ok = QInputDialog.getText(self, tr("dlg.new_title", kind=self._ITEM_KIND), tr("dlg.new_label"))
        if not ok or not name.strip():
            return
        store = self._get_store()
        from storage.markdown_utils import to_slug
        slug = to_slug(name.strip())
        if store.get(slug):
            QMessageBox.warning(self, tr("dlg.exists"), tr("dlg.exists_msg", kind=self._ITEM_KIND.title(), name=name))
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
            self, tr("dlg.delete"), tr("dlg.delete_q", name=item.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            store.delete(self._current_id)
            self._current_id = None
            self.refresh()

    def _on_save(self) -> None:
        if not self._current_id:
            QMessageBox.information(self, tr("dlg.no_select"), tr("dlg.no_select_m"))
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
            self._flash_saved()
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

    def _flash_saved(self) -> None:
        """Briefly turn the Save button green to confirm a successful save."""
        original_text = tr("btn.save")
        self.btn_save.setText(tr("btn.saved"))
        self.btn_save.setStyleSheet(
            "QPushButton { background:#107C10; color:white; border-radius:4px; padding:4px 20px; }"
        )
        def _restore():
            self.btn_save.setText(original_text)
            self.btn_save.setStyleSheet(
                "QPushButton { background:#0063B1; color:white; border-radius:4px; padding:4px 20px; }"
                "QPushButton:hover { background:#0078D4; }"
            )
        QTimer.singleShot(1500, _restore)

    def retranslate_ui(self) -> None:
        """Update translatable widget texts after language change."""
        self.btn_new.setText(tr("btn.new"))
        self.btn_del.setText(tr("btn.delete"))
        self.btn_save.setText(tr("btn.save"))


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
        self._banner_ag = _info_banner(tr("agent.banner"))
        layout.addWidget(self._banner_ag)
        layout.addWidget(_label(tr("agent.form_title")))
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_role = QLineEdit()
        self.f_desc = QPlainTextEdit(); self.f_desc.setMaximumHeight(60)
        self.f_model = QComboBox(); self.f_model.setEditable(True)
        self.f_model.addItems(self._MODELS)
        self._flr_ag_name  = _fl_row(fl, "agent.name",        self.f_name)
        self._flr_ag_role  = _fl_row(fl, "agent.role",        self.f_role)
        self._flr_ag_desc  = _fl_row(fl, "agent.description", self.f_desc)
        self._flr_ag_model = _fl_row(fl, "agent.model",       self.f_model)
        layout.addLayout(fl)

        self._lbl_ag_spec = _label(tr("agent.specialization"))
        layout.addWidget(self._lbl_ag_spec)
        self.f_spec = ListEditor(tr("agent.spec_ph"))
        layout.addWidget(self.f_spec)

        self._lbl_ag_resp = _label(tr("agent.responsibilities"))
        layout.addWidget(self._lbl_ag_resp)
        self.f_resp = ListEditor(tr("agent.resp_ph"))
        layout.addWidget(self.f_resp)

        self._lbl_ag_rules = _label(tr("agent.hard_rules"))
        layout.addWidget(self._lbl_ag_rules)
        self.f_rules = ListEditor(tr("agent.rules_ph"))
        layout.addWidget(self.f_rules)

        self._lbl_ag_patt = _label(tr("agent.preferred_patterns"))
        layout.addWidget(self._lbl_ag_patt)
        self.f_patterns = ListEditor(tr("agent.pat_ph"))
        layout.addWidget(self.f_patterns)

        self._lbl_ag_notes = _label(tr("agent.notes"))
        layout.addWidget(self._lbl_ag_notes)
        self.f_notes = ListEditor(tr("agent.notes_ph"))
        layout.addWidget(self.f_notes)

        self._lbl_ag_skills = _label(tr("agent.skills"))
        layout.addWidget(self._lbl_ag_skills)
        self.f_skills = QListWidget()
        self.f_skills.setMinimumHeight(150)
        self.f_skills.setToolTip("Zaznacz skille używane przez tego agenta")
        layout.addWidget(self.f_skills)

        self._lbl_ag_hooks = _label(tr("agent.hooks"))
        layout.addWidget(self._lbl_ag_hooks)
        self.f_hooks = QListWidget()
        self.f_hooks.setMinimumHeight(120)
        self.f_hooks.setToolTip("Zaznacz hooki przypisane do tego agenta")
        layout.addWidget(self.f_hooks)

        self._lbl_ag_instr = _label(tr("agent.instructions"))
        layout.addWidget(self._lbl_ag_instr)
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

    def retranslate_ui(self) -> None:
        super().retranslate_ui()
        self._flr_ag_name.setText(tr("agent.name") + ":")
        self._flr_ag_role.setText(tr("agent.role") + ":")
        self._flr_ag_desc.setText(tr("agent.description") + ":")
        self._flr_ag_model.setText(tr("agent.model") + ":")
        self._lbl_ag_spec.setText(tr("agent.specialization"))
        self._lbl_ag_resp.setText(tr("agent.responsibilities"))
        self._lbl_ag_rules.setText(tr("agent.hard_rules"))
        self._lbl_ag_patt.setText(tr("agent.preferred_patterns"))
        self._lbl_ag_notes.setText(tr("agent.notes"))
        self._lbl_ag_skills.setText(tr("agent.skills"))
        self._lbl_ag_hooks.setText(tr("agent.hooks"))
        self._lbl_ag_instr.setText(tr("agent.instructions"))
        self._banner_ag.setText(tr("agent.banner"))


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
        self._banner_sk = _info_banner(tr("skill.banner"), color="#EBF5EB", border="#5CB85C")
        layout.addWidget(self._banner_sk)
        self._lbl_sk_title = _label(tr("skill.form_title"))
        layout.addWidget(self._lbl_sk_title)
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
        self._flr_sk_name  = _fl_row(fl, "skill.name",        self.f_name)
        self._flr_sk_desc  = _fl_row(fl, "skill.description", self.f_desc)
        self._flr_sk_phase = _fl_row(fl, "skill.phase",       self.f_phase)
        self._flr_sk_when  = _fl_row(fl, "skill.when_to_use", self.f_when)
        layout.addLayout(fl)

        self._lbl_sk_steps = _label(tr("skill.steps"))
        layout.addWidget(self._lbl_sk_steps)
        self.f_steps = ListEditor(tr("skill.steps_ph"))
        layout.addWidget(self.f_steps)

        self._banner_sk_exit = _info_banner(tr("skill.banner_exit"), color="#F0F9FF", border="#0EA5E9")
        layout.addWidget(self._banner_sk_exit)
        self.f_exit = QPlainTextEdit()
        self.f_exit.setMaximumHeight(65)
        self.f_exit.setPlaceholderText("np. All tests pass, build is clean, no linting errors, reviewer approved…")
        layout.addWidget(self.f_exit)

        self._lbl_sk_rules = _label(tr("skill.rules"))
        layout.addWidget(self._lbl_sk_rules)
        self.f_rules = ListEditor(tr("skill.rules_ph"))
        layout.addWidget(self.f_rules)

        self._banner_sk_anti = _info_banner(tr("skill.banner_anti"), color="#FFF7ED", border="#F97316")
        layout.addWidget(self._banner_sk_anti)
        self.f_anti = ListEditor(tr("skill.anti_ph"))
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
        self._flr_sk_lang = _fl_row(fl2, "skill.lang",          self.f_lang)
        self._flr_sk_out  = _fl_row(fl2, "skill.output_format", self.f_out)
        layout.addLayout(fl2)

        self._lbl_sk_tmpl = _label(tr("skill.template"))
        layout.addWidget(self._lbl_sk_tmpl)
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

    def retranslate_ui(self) -> None:
        super().retranslate_ui()
        self._lbl_sk_title.setText(tr("skill.form_title"))
        self._flr_sk_name.setText(tr("skill.name") + ":")
        self._flr_sk_desc.setText(tr("skill.description") + ":")
        self._flr_sk_phase.setText(tr("skill.phase") + ":")
        self._flr_sk_when.setText(tr("skill.when_to_use") + ":")
        self._lbl_sk_steps.setText(tr("skill.steps"))
        self._lbl_sk_rules.setText(tr("skill.rules"))
        self._flr_sk_lang.setText(tr("skill.lang") + ":")
        self._flr_sk_out.setText(tr("skill.output_format") + ":")
        self._lbl_sk_tmpl.setText(tr("skill.template"))
        self._banner_sk.setText(tr("skill.banner"))
        self._banner_sk_exit.setText(tr("skill.banner_exit"))
        self._banner_sk_anti.setText(tr("skill.banner_anti"))


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
        self._banner_hk = _info_banner(tr("hook.banner"), color="#FFF8E1", border="#F0AD4E")
        layout.addWidget(self._banner_hk)
        self._lbl_hk_title = _label(tr("hook.form_title"))
        layout.addWidget(self._lbl_hk_title)
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_desc = QPlainTextEdit(); self.f_desc.setMaximumHeight(60)

        self.f_trigger = QComboBox(); self.f_trigger.setEditable(True)
        self.f_trigger.addItems(self._TRIGGERS)
        self.f_trigger.setCurrentIndex(-1)
        self.f_trigger.lineEdit().setPlaceholderText(tr("hook.trigger_ph"))

        self.f_failure = QLineEdit()

        self.f_event = QComboBox()
        self.f_event.addItems(self._EVENTS)
        self.f_type = QComboBox()
        self.f_type.addItems(self._TYPES)
        self.f_priority = QSpinBox()
        self.f_priority.setRange(0, 9999); self.f_priority.setValue(100)

        self._flr_hk_name     = _fl_row(fl, "hook.name",        self.f_name)
        self._flr_hk_desc     = _fl_row(fl, "hook.description", self.f_desc)
        self._flr_hk_trigger  = _fl_row(fl, "hook.trigger",     self.f_trigger)
        self._flr_hk_failure  = _fl_row(fl, "hook.on_failure",  self.f_failure)
        self._flr_hk_event    = _fl_row(fl, "hook.event",       self.f_event)
        self._flr_hk_type     = _fl_row(fl, "hook.type",        self.f_type)
        self._flr_hk_priority = _fl_row(fl, "hook.priority",    self.f_priority)
        layout.addLayout(fl)

        self._lbl_hk_files = _label(tr("hook.for_files"))
        layout.addWidget(self._lbl_hk_files)
        self.f_files = ListEditor(tr("hook.files_ph"))
        layout.addWidget(self.f_files)

        self._lbl_hk_checks = _label(tr("hook.checks"))
        layout.addWidget(self._lbl_hk_checks)
        self.f_checks = ListEditor(tr("hook.checks_ph"))
        layout.addWidget(self.f_checks)

        self._lbl_hk_actions = _label(tr("hook.actions"))
        layout.addWidget(self._lbl_hk_actions)
        self.f_actions = ListEditor(tr("hook.actions_ph"))
        layout.addWidget(self.f_actions)

        self._lbl_hk_notes = _label(tr("hook.notes"))
        layout.addWidget(self._lbl_hk_notes)
        self.f_notes = ListEditor(tr("hook.notes_ph"))
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

    def retranslate_ui(self) -> None:
        super().retranslate_ui()
        self._lbl_hk_title.setText(tr("hook.form_title"))
        self._flr_hk_name.setText(tr("hook.name") + ":")
        self._flr_hk_desc.setText(tr("hook.description") + ":")
        self._flr_hk_trigger.setText(tr("hook.trigger") + ":")
        self._flr_hk_failure.setText(tr("hook.on_failure") + ":")
        self._flr_hk_event.setText(tr("hook.event") + ":")
        self._flr_hk_type.setText(tr("hook.type") + ":")
        self._flr_hk_priority.setText(tr("hook.priority") + ":")
        self._lbl_hk_files.setText(tr("hook.for_files"))
        self._lbl_hk_checks.setText(tr("hook.checks"))
        self._lbl_hk_actions.setText(tr("hook.actions"))
        self._lbl_hk_notes.setText(tr("hook.notes"))
        self._banner_hk.setText(tr("hook.banner"))


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
        self.btn_new = QPushButton(tr("btn.new"))
        self.btn_del = QPushButton(tr("btn.delete"))
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
        self.btn_save = QPushButton(tr("btn.save"))
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
        self._banner_in = _info_banner(tr("instr.banner"), color="#F5E6FF", border="#9B59B6")
        layout.addWidget(self._banner_in)
        self._lbl_in_title = _label(tr("instr.form_title"))
        layout.addWidget(self._lbl_in_title)
        layout.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.f_name = QLineEdit(); self.f_name.setReadOnly(True)
        self.f_apply = QComboBox(); self.f_apply.setEditable(True)
        self.f_apply.setPlaceholderText("np. **/*.ts  lub  ** (puste = brak applyTo)")
        self.f_apply.addItems([""] + self._APPLY_PRESETS)
        self.f_apply.setCurrentIndex(0)
        self._flr_in_name  = _fl_row(fl, "instr.name",     self.f_name)
        self._flr_in_apply = _fl_row(fl, "instr.apply_to", self.f_apply)
        layout.addLayout(fl)
        layout.addWidget(_sep())

        # Inner splitter: sections navigator | editor
        inner = QSplitter(Qt.Orientation.Horizontal)

        nav = QWidget(); nav.setMaximumWidth(210)
        nv = QVBoxLayout(nav); nv.setContentsMargins(0, 0, 4, 0); nv.setSpacing(4)
        self._lbl_in_sections = _label(tr("instr.sections"))
        nv.addWidget(self._lbl_in_sections)
        self.f_sections = QListWidget()
        nv.addWidget(self.f_sections, 1)
        self.btn_add_sec = QPushButton(tr("instr.add_section"))
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

    def retranslate_ui(self) -> None:
        self.btn_new.setText(tr("btn.new"))
        self.btn_del.setText(tr("btn.delete"))
        self.btn_save.setText(tr("btn.save"))
        self._lbl_in_title.setText(tr("instr.form_title"))
        self._flr_in_name.setText(tr("instr.name") + ":")
        self._flr_in_apply.setText(tr("instr.apply_to") + ":")
        self._lbl_in_sections.setText(tr("instr.sections"))
        self.btn_add_sec.setText(tr("instr.add_section"))
        self._banner_in.setText(tr("instr.banner"))


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
        self.btn_refresh = QPushButton(tr("valid.run"))
        self.btn_refresh.setFixedHeight(28)
        self.btn_refresh.setFixedWidth(110)
        self.btn_refresh.clicked.connect(self._refresh_agents)
        top.addWidget(self.btn_refresh)

        self._hint_lbl = QLabel(tr("valid.hint"))
        self._hint_lbl.setStyleSheet("color:#777; font-size:11px;")
        self._hint_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top.addSpacing(8)
        top.addWidget(self._hint_lbl)
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
        self._agent_hdr = QLabel(f"<b>{tr('valid.agents_hdr')}</b>")
        self._agent_hdr.setStyleSheet("font-size:12px; padding:2px 0;")
        lv.addWidget(self._agent_hdr)
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
        self._issues_hdr = QLabel(f"<b>{tr('valid.issues_hdr')}</b>")
        self._issues_hdr.setStyleSheet("font-size:12px; padding:2px 0;")
        rv.addWidget(self._issues_hdr)
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
        all_item = QListWidgetItem(tr("valid.all"))
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
            item = QListWidgetItem(tr("valid.ok"))
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

    def retranslate_ui(self) -> None:
        self.btn_refresh.setText(tr("valid.run"))
        self._hint_lbl.setText(tr("valid.hint"))
        self._agent_hdr.setText(f"<b>{tr('valid.agents_hdr')}</b>")
        self._issues_hdr.setText(f"<b>{tr('valid.issues_hdr')}</b>")
        # Refresh the list so "All" text uses new language
        self._refresh_agents()
