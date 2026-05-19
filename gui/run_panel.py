"""Run Panel — executes an agent via runtime/runner.py in a background thread."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)
from gui.i18n import tr


def _banner(text: str, color: str = "#F0F4FF", border: str = "#5B7FD9") -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setTextFormat(Qt.TextFormat.RichText)
    lbl.setStyleSheet(
        f"background:{color}; border-left:4px solid {border};"
        " border-radius:3px; padding:6px 10px;"
        " color:#333; font-size:11px; margin-bottom:4px;"
    )
    return lbl


class _RunWorker(QThread):
    """Calls run_agent() in a background thread."""

    finished = pyqtSignal(object)   # RunResult
    errored  = pyqtSignal(str)

    def __init__(self, agent, user_input: str, skills: list, hooks: list) -> None:
        super().__init__()
        self._agent      = agent
        self._user_input = user_input
        self._skills     = skills
        self._hooks      = hooks

    def run(self) -> None:
        try:
            from runtime.runner import run_agent
            result = run_agent(
                self._agent, self._user_input,
                skills=self._skills, hooks=self._hooks,
            )
            self.finished.emit(result)
        except Exception as exc:
            self.errored.emit(str(exc))


class RunPanel(QWidget):
    """Tab for running an agent with a user-supplied prompt."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: _RunWorker | None = None
        self._build_ui()
        self._refresh_agents()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        self._banner = _banner(tr("run.banner"))
        v.addWidget(self._banner)

        # ── agent selector ────────────────────────────────────────────────────
        top = QHBoxLayout()
        self._lbl_agent = QLabel(tr("run.agent_lbl"))
        top.addWidget(self._lbl_agent)
        self.agent_combo = QComboBox()
        self.agent_combo.setMinimumWidth(220)
        top.addWidget(self.agent_combo)

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedWidth(28)
        self.refresh_btn.setToolTip("Odśwież listę agentów")
        self.refresh_btn.clicked.connect(self._refresh_agents)
        top.addWidget(self.refresh_btn)
        top.addStretch()

        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("color:#555; font-size:11px;")
        top.addWidget(self.status_lbl)
        v.addLayout(top)

        # ── splitter: input / output ──────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)

        # input widget
        input_w = QWidget()
        iv = QVBoxLayout(input_w)
        iv.setContentsMargins(0, 0, 0, 0)
        iv.setSpacing(4)
        self._lbl_task = QLabel(tr("run.task_lbl"))
        iv.addWidget(self._lbl_task)
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText(tr("run.input_ph"))
        self.input_edit.setMinimumHeight(90)
        iv.addWidget(self.input_edit)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton(tr("btn.run"))
        self.run_btn.setFixedHeight(32)
        self.run_btn.setStyleSheet(
            "QPushButton { background:#0063B1; color:white; border-radius:4px; padding:4px 20px; }"
            "QPushButton:hover { background:#0078D4; }"
        )
        self.run_btn.clicked.connect(self._on_run)

        self.cancel_btn = QPushButton(tr("btn.stop"))
        self.cancel_btn.setFixedHeight(32)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._on_cancel)

        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        iv.addLayout(btn_row)

        # output widget
        output_w = QWidget()
        ov = QVBoxLayout(output_w)
        ov.setContentsMargins(0, 0, 0, 0)
        ov.setSpacing(4)
        hdr = QHBoxLayout()
        self._lbl_output = QLabel(tr("run.output_lbl"))
        hdr.addWidget(self._lbl_output)
        hdr.addStretch()
        self.copy_btn = QPushButton(tr("btn.copy"))
        self.copy_btn.setFixedHeight(24)
        self.copy_btn.clicked.connect(self._on_copy)
        hdr.addWidget(self.copy_btn)
        ov.addLayout(hdr)

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText(tr("run.output_ph"))
        self.output_edit.setStyleSheet(
            "background:#FAFAFA; font-family:Consolas,monospace; font-size:12px;"
        )
        ov.addWidget(self.output_edit)

        splitter.addWidget(input_w)
        splitter.addWidget(output_w)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        v.addWidget(splitter)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _refresh_agents(self) -> None:
        self.agent_combo.clear()
        try:
            from gui.state import get_registry
            for agent in get_registry().agents.list():
                self.agent_combo.addItem(agent.name, userData=agent.id)
        except Exception:
            pass

    def _set_status(self, msg: str, error: bool = False) -> None:
        self.status_lbl.setText(msg)
        color = "#C0392B" if error else "#555555"
        self.status_lbl.setStyleSheet(f"color:{color}; font-size:11px;")

    def _reset_ui(self) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None

    def retranslate_ui(self) -> None:
        self._lbl_agent.setText(tr("run.agent_lbl"))
        self._lbl_task.setText(tr("run.task_lbl"))
        self._lbl_output.setText(tr("run.output_lbl"))
        self.run_btn.setText(tr("btn.run"))
        self.cancel_btn.setText(tr("btn.stop"))
        self.copy_btn.setText(tr("btn.copy"))
        self._banner.setText(tr("run.banner"))

    # ── slots ─────────────────────────────────────────────────────────────────

    def _on_run(self) -> None:
        agent_id   = self.agent_combo.currentData()
        user_input = self.input_edit.toPlainText().strip()
        if not agent_id:
            self._set_status("Wybierz agenta.", error=True)
            return
        if not user_input:
            self._set_status("Wpisz zadanie.", error=True)
            return

        try:
            from gui.state import get_registry
            reg    = get_registry()
            agent  = reg.agents.get(agent_id)
            skills = [reg.skills.get(sid) for sid in agent.skill_ids if reg.skills.get(sid)]
            hooks  = [reg.hooks.get(hid)  for hid in agent.hook_ids  if reg.hooks.get(hid)]
        except Exception as exc:
            self._set_status(f"Błąd ładowania: {exc}", error=True)
            return

        self.output_edit.setPlainText("")
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self._set_status("Uruchamianie…")

        # Reload saved API keys into os.environ and litellm right before each run
        import os
        import litellm
        from gui.settings_panel import _load_api_keys_file
        _LITELLM_ATTRS: dict[str, str] = {
            "OPENAI_API_KEY":    "openai_key",
            "ANTHROPIC_API_KEY": "anthropic_key",
            "GEMINI_API_KEY":    "gemini_key",
        }
        for k, v in _load_api_keys_file().items():
            if v:
                os.environ[k] = v
                if k in _LITELLM_ATTRS:
                    setattr(litellm, _LITELLM_ATTRS[k], v)

        self._last_model = agent.model or "gpt-4o"
        self._worker = _RunWorker(agent, user_input, skills, hooks)
        self._worker.finished.connect(self._on_done)
        self._worker.errored.connect(self._on_error)
        self._worker.start()

    def _on_done(self, result) -> None:
        lines: list[str] = []
        model_used = getattr(self, "_last_model", "?")
        lines.append(f"[Model: {model_used}]")
        lines.append("")
        if result.skill_calls:
            lines.append("=== Wywołania skilli ===")
            for sc in result.skill_calls:
                lines.append(f"  • {sc.get('skill', '?')}: {sc.get('result', '')}")
            lines.append("")
        lines.append(result.output or "(brak odpowiedzi)")
        if result.error:
            lines.append(f"\n[BŁĄD]: {result.error}")
        self.output_edit.setPlainText("\n".join(lines))
        self._reset_ui()
        self._set_status("Gotowe.")

    def _on_error(self, msg: str) -> None:
        self.output_edit.setPlainText(f"[BŁĄD WYKONANIA]\n\n{msg}")
        self._reset_ui()
        self._set_status("Błąd wykonania.", error=True)

    def _on_cancel(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait(500)
        self._reset_ui()
        self._set_status("Anulowano.")

    def _on_copy(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.output_edit.toPlainText())
