"""Run Panel — streaming conversation with an agent via runtime/runner.py."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy, QSplitter, QVBoxLayout, QWidget,
)
from gui.i18n import tr

_SESSION_DIR = Path("data/sessions")


def _banner(text: str, color: str = "#F0F4FF", border: str = "#5B7FD9") -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setTextFormat(Qt.TextFormat.RichText)
    lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    lbl.setStyleSheet(
        f"background:{color}; border-left:4px solid {border};"
        " border-radius:3px; padding:6px 10px;"
        " color:#333; font-size:11px; margin-bottom:4px;"
    )
    return lbl


# ── Background workers ────────────────────────────────────────────────────────

class _StreamWorker(QThread):
    chunk_received = pyqtSignal(str)
    tool_called    = pyqtSignal(str, str)
    done           = pyqtSignal(object)
    errored        = pyqtSignal(str)

    def __init__(self, agent, user_input: str, skills: list, hooks: list,
                 history: list) -> None:
        super().__init__()
        self._agent      = agent
        self._user_input = user_input
        self._skills     = skills
        self._hooks      = hooks
        self._history    = history

    def run(self) -> None:
        try:
            from runtime.runner import run_agent_stream
            for event in run_agent_stream(
                self._agent, self._user_input,
                skills=self._skills, hooks=self._hooks,
                history=self._history,
            ):
                t = event["type"]
                if t == "text":
                    self.chunk_received.emit(event["content"])
                elif t == "tool_call":
                    self.tool_called.emit(event["skill"], event["result"])
                elif t == "done":
                    self.done.emit(event["result"])
                elif t == "error":
                    self.errored.emit(event["content"])
                    return
        except Exception as exc:
            self.errored.emit(str(exc))


class _TtsWorker(QThread):
    tts_error   = pyqtSignal(str)
    tts_started = pyqtSignal()   # fired just before audio begins playing

    def __init__(self, text: str, api_key: str, voice: str = "alloy") -> None:
        super().__init__()
        self._text    = text
        self._api_key = api_key
        self._voice   = voice
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except Exception:
            pass

    def run(self) -> None:
        import os, tempfile
        tmp_path: str | None = None
        try:
            from openai import OpenAI
            client   = OpenAI(api_key=self._api_key)
            response = client.audio.speech.create(
                model="tts-1", voice=self._voice, input=self._text
            )
            if self._stopped:
                return
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(response.content)
                tmp_path = f.name
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            self.tts_started.emit()
            while pygame.mixer.music.get_busy() and not self._stopped:
                pygame.time.wait(50)
            pygame.mixer.music.unload()
        except Exception as exc:
            self.tts_error.emit(str(exc))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass


# ── Per-turn widget ───────────────────────────────────────────────────────────

class _TurnWidget(QWidget):
    speak_requested = pyqtSignal(str)
    stop_requested  = pyqtSignal()

    def __init__(self, turn_num: int, user_in: str, agent_out: str,
                 model: str, tool_calls: list,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(2)

        # User line
        preview = user_in[:90] + ("…" if len(user_in) > 90 else "")
        user_lbl = QLabel(f"👤 Ty (#{turn_num}):   {preview}")
        user_lbl.setStyleSheet("color:#666; font-size:11px; padding:2px 4px;")
        user_lbl.setWordWrap(True)
        layout.addWidget(user_lbl)

        # Tool calls
        for tc in tool_calls:
            name = tc.get("skill", "") if isinstance(tc, dict) else ""
            res  = str(tc.get("result", ""))[:100] if isinstance(tc, dict) else ""
            tc_lbl = QLabel(f"  ⚙ {name} → {res}")
            tc_lbl.setStyleSheet("color:#999; font-size:10px; padding:1px 4px;")
            layout.addWidget(tc_lbl)

        # Agent header row
        agent_hdr = QHBoxLayout()
        agent_hdr.setContentsMargins(0, 4, 0, 2)
        agent_lbl = QLabel(f"🤖 Agent [{model}]:")
        agent_lbl.setStyleSheet(
            "font-weight:bold; font-size:11px; color:#333; padding:0 4px;"
        )
        agent_hdr.addWidget(agent_lbl)
        agent_hdr.addStretch()

        self._speak_btn = QPushButton("▶")
        self._speak_btn.setFixedSize(34, 24)
        self._speak_btn.setCheckable(True)
        self._speak_btn.setToolTip("Czytaj odpowiedź (TTS)")
        self._speak_btn.setStyleSheet(self._STYLE_IDLE)
        self._speak_btn.clicked.connect(self._on_speak_clicked)
        agent_hdr.addWidget(self._speak_btn)
        layout.addLayout(agent_hdr)
        self._is_loading = False

        # Response text
        self._text_edit = QLabel()
        self._text_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._text_edit.setWordWrap(True)
        self._text_edit.setText(agent_out)
        self._text_edit.setStyleSheet(
            "background: #FAFAFA; font-family: Consolas, monospace;"
            " font-size: 12px; border: none; padding: 4px 4px 8px 4px;"
        )
        self._text_edit.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        layout.addWidget(self._text_edit)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e0e0e0; margin-top: 6px;")
        layout.addWidget(line)

        self._agent_out = agent_out

    _STYLE_IDLE = (
        "QPushButton { border:1px solid #ccc; border-radius:4px;"
        "  font-size:11px; background:#fff; }"
        "QPushButton:hover { background:#e8f0fe; }"
    )
    _STYLE_LOADING = (
        "QPushButton { border:1px solid #f0a030; border-radius:4px;"
        "  font-size:13px; background:#fff8e1; }"
        "QPushButton:hover { background:#ffe082; }"
    )
    _STYLE_PLAYING = (
        "QPushButton { border:1px solid #4CAF50; border-radius:4px;"
        "  font-size:11px; background:#e8f4e8; color:#2e7d32; }"
        "QPushButton:hover { background:#c8e6c9; }"
    )

    @property
    def agent_text(self) -> str:
        return self._agent_out

    def _on_speak_clicked(self) -> None:
        if self._speak_btn.isChecked():
            self.speak_requested.emit(self._agent_out)
        else:
            self.stop_requested.emit()

    def set_loading(self, active: bool) -> None:
        self._is_loading = active
        self._speak_btn.blockSignals(True)
        self._speak_btn.setChecked(active)
        self._speak_btn.setText("⏳" if active else "▶")
        self._speak_btn.setStyleSheet(
            self._STYLE_LOADING if active else self._STYLE_IDLE
        )
        self._speak_btn.setToolTip(
            "Ładowanie… (kliknij aby anulować)" if active else "Czytaj odpowiedź (TTS)"
        )
        self._speak_btn.blockSignals(False)

    def set_speaking(self, active: bool) -> None:
        self._is_loading = False
        self._speak_btn.blockSignals(True)
        self._speak_btn.setChecked(active)
        self._speak_btn.setText("■" if active else "▶")
        self._speak_btn.setStyleSheet(
            self._STYLE_PLAYING if active else self._STYLE_IDLE
        )
        self._speak_btn.setToolTip(
            "Zatrzymaj czytanie" if active else "Czytaj odpowiedź (TTS)"
        )
        self._speak_btn.blockSignals(False)


# ── Main panel ────────────────────────────────────────────────────────────────

class RunPanel(QWidget):
    _DIVIDER = "─" * 54

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker:             _StreamWorker | None = None
        self._tts_worker:         _TtsWorker | None    = None
        self._active_turn_widget: _TurnWidget | None   = None
        self._turn_widgets:       list[_TurnWidget]    = []
        # live conversation state
        self._history:            list[dict]                       = []
        self._display_turns:      list[tuple[str, str, str, list]] = []
        self._last_model:         str                               = "?"
        self._current_input:      str                               = ""
        self._current_tool_calls: list[dict]                        = []
        self._current_agent_id:   str                               = ""
        self._current_agent_name: str                               = ""
        self._current_session_id: str | None                        = None
        self._current_session_ts: str | None                        = None
        # session store
        from storage.store import JsonStore
        from core.session import Session
        self._session_store: JsonStore = JsonStore(_SESSION_DIR, Session)
        self._build_ui()
        self._refresh_agents()
        self._refresh_sessions()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        self._banner = _banner(tr("run.banner"))
        v.addWidget(self._banner)

        # top bar
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
        self.new_conv_btn = QPushButton(tr("run.new_conv"))
        self.new_conv_btn.setFixedHeight(26)
        self.new_conv_btn.clicked.connect(self._on_new_conv)
        top.addWidget(self.new_conv_btn)
        top.addStretch()
        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("color:#555; font-size:11px;")
        top.addWidget(self.status_lbl)
        v.addLayout(top)

        # horizontal splitter: sessions | main
        h_splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT: sessions sidebar
        sessions_w = QWidget()
        sv = QVBoxLayout(sessions_w)
        sv.setContentsMargins(0, 0, 4, 0)
        sv.setSpacing(4)
        self._lbl_sessions = QLabel(tr("run.sessions_lbl"))
        self._lbl_sessions.setStyleSheet(
            "font-weight:bold; font-size:11px; color:#333;"
        )
        sv.addWidget(self._lbl_sessions)
        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet(
            "QListWidget { font-size:10px; background:#F7F7F7; }"
            "QListWidget::item { padding:4px 2px; border-bottom:1px solid #E0E0E0; }"
            "QListWidget::item:selected { background:#D0E4F7; color:#000; }"
        )
        self.sessions_list.currentItemChanged.connect(self._on_session_selected)
        sv.addWidget(self.sessions_list)
        self.del_session_btn = QPushButton(tr("run.session_del"))
        self.del_session_btn.setFixedHeight(24)
        self.del_session_btn.clicked.connect(self._on_session_delete)
        sv.addWidget(self.del_session_btn)

        # RIGHT
        right_w = QWidget()
        rv = QVBoxLayout(right_w)
        rv.setContentsMargins(4, 0, 0, 0)
        rv.setSpacing(0)

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
        self.input_edit.setMinimumHeight(80)
        self.input_edit.setMaximumHeight(140)
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

        # scroll area for completed turn widgets
        self._turns_scroll = QScrollArea()
        self._turns_scroll.setWidgetResizable(True)
        self._turns_scroll.setStyleSheet(
            "QScrollArea { border: none; background: #FAFAFA; }"
        )
        self._turns_container = QWidget()
        self._turns_container.setStyleSheet("background: #FAFAFA;")
        self._turns_layout = QVBoxLayout(self._turns_container)
        self._turns_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._turns_layout.setContentsMargins(4, 4, 4, 4)
        self._turns_layout.setSpacing(0)
        self._turns_scroll.setWidget(self._turns_container)
        ov.addWidget(self._turns_scroll)

        # live streaming text (visible only during a run)
        self._live_edit = QPlainTextEdit()
        self._live_edit.setReadOnly(True)
        self._live_edit.setPlaceholderText(tr("run.output_ph"))
        self._live_edit.setStyleSheet(
            "background: #FAFAFA; font-family: Consolas, monospace;"
            " font-size: 12px; border-top: 1px solid #e0e0e0;"
        )
        self._live_edit.setMinimumHeight(60)
        self._live_edit.setMaximumHeight(300)
        self._live_edit.hide()
        ov.addWidget(self._live_edit)

        splitter.addWidget(input_w)
        splitter.addWidget(output_w)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        rv.addWidget(splitter)

        h_splitter.addWidget(sessions_w)
        h_splitter.addWidget(right_w)
        h_splitter.setStretchFactor(0, 0)
        h_splitter.setStretchFactor(1, 1)
        h_splitter.setSizes([200, 700])
        v.addWidget(h_splitter, stretch=1)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _refresh_agents(self) -> None:
        self.agent_combo.clear()
        try:
            from gui.state import get_registry
            for agent in get_registry().agents.list():
                self.agent_combo.addItem(agent.name, userData=agent.id)
        except Exception:
            pass

    def _refresh_sessions(self) -> None:
        self.sessions_list.blockSignals(True)
        self.sessions_list.clear()
        try:
            sessions = sorted(
                self._session_store.list(),
                key=lambda s: s.created_at,
                reverse=True,
            )
            for session in sessions:
                item = QListWidgetItem(session.label)
                item.setData(Qt.ItemDataRole.UserRole, session.id)
                self.sessions_list.addItem(item)
        except Exception:
            pass
        self.sessions_list.blockSignals(False)

    def _set_status(self, msg: str, error: bool = False) -> None:
        self.status_lbl.setText(msg)
        color = "#C0392B" if error else "#555555"
        self.status_lbl.setStyleSheet(f"color:{color}; font-size:11px;")

    def _reset_ui(self) -> None:
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._worker = None

    def _append(self, text: str) -> None:
        cursor = self._live_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._live_edit.setTextCursor(cursor)
        self._live_edit.insertPlainText(text)
        self._live_edit.ensureCursorVisible()

    def _clear_turns(self) -> None:
        for tw in self._turn_widgets:
            self._turns_layout.removeWidget(tw)
            tw.deleteLater()
        self._turn_widgets.clear()

    def _add_turn_widget(self, turn_num: int, user_in: str, agent_out: str,
                         model: str, tool_calls: list) -> "_TurnWidget":
        tw = _TurnWidget(turn_num, user_in, agent_out, model, tool_calls)
        tw.speak_requested.connect(lambda text, w=tw: self._speak(text, w))
        tw.stop_requested.connect(self._stop_tts)
        self._turns_layout.addWidget(tw)
        self._turn_widgets.append(tw)
        QTimer.singleShot(0, lambda: self._turns_scroll.verticalScrollBar().setValue(
            self._turns_scroll.verticalScrollBar().maximum()
        ))
        return tw

    def _render_turns(self, turns: list) -> None:
        self._clear_turns()
        for i, turn in enumerate(turns, 1):
            if isinstance(turn, tuple):
                user_in, agent_out, model_used, tcs = turn
            else:
                user_in    = turn.user_input
                agent_out  = turn.agent_output
                model_used = turn.model
                tcs = [
                    {"skill": tc.get("skill", ""), "result": tc.get("result", "")}
                    if isinstance(tc, dict) else {"skill": "", "result": ""}
                    for tc in turn.tool_calls
                ]
            self._add_turn_widget(i, user_in, agent_out, model_used, tcs)

    def _render_history(self) -> None:
        self._render_turns(self._display_turns)

    def _speak(self, text: str, widget: "_TurnWidget") -> None:
        from gui.settings_panel import _load_api_keys_file
        api_key = _load_api_keys_file().get("OPENAI_API_KEY", "")
        if not api_key:
            self._set_status("TTS: brak klucza OpenAI w Ustawieniach", error=True)
            widget.set_speaking(False)
            return
        self._stop_tts()
        self._active_turn_widget = widget
        widget.set_loading(True)          # ⏳ immediately on click
        self._tts_worker = _TtsWorker(text, api_key)
        self._tts_worker.tts_started.connect(
            lambda w=widget: (w.set_loading(False), w.set_speaking(True))
        )
        self._tts_worker.finished.connect(self._on_tts_finished)
        self._tts_worker.tts_error.connect(
            lambda msg, w=widget: (
                self._set_status(f"TTS b\u0142\u0105d: {msg}", error=True),
                w.set_loading(False),
                w.set_speaking(False),
            )
        )
        self._tts_worker.start()

    def _stop_tts(self) -> None:
        if self._tts_worker is not None:
            self._tts_worker.stop()
            if not self._tts_worker.wait(2000):
                self._tts_worker.terminate()
                self._tts_worker.wait(300)
        self._tts_worker = None
        if self._active_turn_widget is not None:
            self._active_turn_widget.set_loading(False)
            self._active_turn_widget.set_speaking(False)
            self._active_turn_widget = None

    def _on_tts_finished(self) -> None:
        self._tts_worker = None
        if self._active_turn_widget is not None:
            self._active_turn_widget.set_speaking(False)
            self._active_turn_widget = None

    def _save_current_session(self) -> None:
        if not self._display_turns or not self._current_agent_id:
            return
        from core.session import Session, SessionTurn
        now = datetime.now(timezone.utc)
        if self._current_session_id is None:
            self._current_session_id = now.strftime("%Y%m%d_%H%M%S")
            self._current_session_ts = now.isoformat()
        turns = [
            SessionTurn(user_input=u, agent_output=a, model=m, tool_calls=tc)
            for u, a, m, tc in self._display_turns
        ]
        session = Session(
            id=self._current_session_id,
            agent_id=self._current_agent_id,
            agent_name=self._current_agent_name,
            created_at=self._current_session_ts or now.isoformat(),
            turns=turns,
        )
        self._session_store.save(session)
        self._refresh_sessions()

    def retranslate_ui(self) -> None:
        self._lbl_agent.setText(tr("run.agent_lbl"))
        self._lbl_task.setText(tr("run.task_lbl"))
        self._lbl_output.setText(tr("run.output_lbl"))
        self._lbl_sessions.setText(tr("run.sessions_lbl"))
        self.run_btn.setText(tr("btn.run"))
        self.cancel_btn.setText(tr("btn.stop"))
        self.copy_btn.setText(tr("btn.copy"))
        self.new_conv_btn.setText(tr("run.new_conv"))
        self.del_session_btn.setText(tr("run.session_del"))
        self._banner.setText(tr("run.banner"))

    # ── slots ─────────────────────────────────────────────────────────────────

    def _on_new_conv(self) -> None:
        self._save_current_session()
        self._history.clear()
        self._display_turns.clear()
        self._current_session_id = None
        self._current_session_ts = None
        self._clear_turns()
        self._live_edit.clear()
        self._live_edit.hide()
        self._set_status("")
        self.sessions_list.blockSignals(True)
        self.sessions_list.clearSelection()
        self.sessions_list.blockSignals(False)

    def _on_session_selected(self, current, previous) -> None:
        if current is None:
            return
        session_id = current.data(Qt.ItemDataRole.UserRole)
        session = self._session_store.get(session_id)
        if session is None:
            return
        self._render_turns(session.turns)

    def _on_session_delete(self) -> None:
        item = self.sessions_list.currentItem()
        if item is None:
            return
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if session_id == self._current_session_id:
            self._current_session_id = None
            self._current_session_ts = None
        self._session_store.delete(session_id)
        self._refresh_sessions()
        self._clear_turns()

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

        import os
        import litellm
        from gui.settings_panel import _load_api_keys_file
        _LITELLM_ATTRS = {
            "OPENAI_API_KEY":    "openai_key",
            "ANTHROPIC_API_KEY": "anthropic_key",
            "GEMINI_API_KEY":    "gemini_key",
        }
        for k, v in _load_api_keys_file().items():
            if v:
                os.environ[k] = v
                if k in _LITELLM_ATTRS:
                    setattr(litellm, _LITELLM_ATTRS[k], v)

        self._last_model         = agent.model or "gpt-4o"
        self._current_input      = user_input
        self._current_tool_calls = []
        self._current_agent_id   = agent.id
        self._current_agent_name = agent.name

        self.sessions_list.blockSignals(True)
        self.sessions_list.clearSelection()
        self.sessions_list.blockSignals(False)

        # show live streaming area
        self._live_edit.clear()
        self._live_edit.show()
        turn_num = len(self._display_turns) + 1
        self._live_edit.appendPlainText(f"{tr('run.turn_you')} (#{turn_num}):")
        self._live_edit.appendPlainText(user_input)
        self._live_edit.appendPlainText("")
        self._live_edit.appendPlainText(f"{tr('run.turn_agent')} [{self._last_model}]:")

        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self._set_status("Uruchamianie...")

        self._worker = _StreamWorker(agent, user_input, skills, hooks, list(self._history))
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.tool_called.connect(self._on_tool_called)
        self._worker.done.connect(self._on_done)
        self._worker.errored.connect(self._on_error)
        self._worker.start()

    def _on_chunk(self, text: str) -> None:
        self._append(text)

    def _on_tool_called(self, skill_name: str, result: str) -> None:
        preview = result[:120] + ("..." if len(result) > 120 else "")
        self._append(f"\n  {tr('run.tool_call')}: {skill_name} -> {preview}\n")
        self._current_tool_calls.append({"skill": skill_name, "result": result})

    def _on_done(self, result) -> None:
        agent_out = result.output or tr("run.no_response")
        turn_num  = len(self._display_turns) + 1
        self._display_turns.append((
            self._current_input,
            agent_out,
            self._last_model,
            list(self._current_tool_calls),
        ))
        self._history = list(result.history_out)

        # hide live edit, create proper turn widget
        self._live_edit.clear()
        self._live_edit.hide()
        self._add_turn_widget(
            turn_num, self._current_input, agent_out,
            self._last_model, list(self._current_tool_calls),
        )

        self.input_edit.clear()
        self._reset_ui()
        self._set_status("Gotowe.")
        self._save_current_session()

    def _on_error(self, msg: str) -> None:
        self._append(f"\n[BŁĄD]: {msg}")
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
        lines: list[str] = []
        for i, (u, a, m, _) in enumerate(self._display_turns, 1):
            if i > 1:
                lines.append(self._DIVIDER)
            lines.append(f"Ty (#{i}): {u}")
            lines.append(f"Agent [{m}]: {a}")
        QApplication.clipboard().setText("\n".join(lines))
