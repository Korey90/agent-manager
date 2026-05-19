"""Settings Panel — language, default model, workspace, API keys."""
from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

import gui.settings as settings
from gui.i18n import tr, set_lang, get_lang, lang_signals

_API_KEYS_FILE = Path.home() / ".agent-manager" / "api_keys.env"

_API_KEYS: list[tuple[str, str]] = [
    ("OPENAI_API_KEY",     "OpenAI"),
    ("ANTHROPIC_API_KEY",  "Anthropic"),
    ("GEMINI_API_KEY",     "Google Gemini"),
]


def _load_api_keys_file() -> dict[str, str]:
    """Read key=value pairs from api_keys.env; ignore comments and blank lines."""
    result: dict[str, str] = {}
    if not _API_KEYS_FILE.exists():
        return result
    for line in _API_KEYS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _save_api_keys_file(keys: dict[str, str]) -> None:
    """Write key=value pairs to api_keys.env (only non-empty values)."""
    _API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Agent Manager — API keys\n# Generated automatically — do not commit.\n"]
    for k, v in keys.items():
        if v:
            lines.append(f"{k}={v}\n")
    _API_KEYS_FILE.write_text("".join(lines), encoding="utf-8")


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFrameShadow(QFrame.Shadow.Sunken)
    return f


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-weight:bold; font-size:12px; color:#333;"
        " border-bottom:1px solid #CCC; padding-bottom:2px; margin-top:8px;"
    )
    return lbl


class SettingsPanel(QWidget):
    """⚙ Ustawienia — język, model, workspace."""

    _LANGS = [("pl", "settings.lang_pl"), ("en", "settings.lang_en")]
    _MODELS = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo",
        "claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-3-5",
        "gemini/gemini-2.0-flash", "ollama/llama3",
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._load_values()
        lang_signals().changed.connect(self.retranslate_ui)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(8)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── section: General ──────────────────────────────────────────────────
        self._lbl_section_general = _section_label(tr("settings.section_general"))
        root.addWidget(self._lbl_section_general)
        root.addWidget(_sep())

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl.setHorizontalSpacing(16)
        fl.setVerticalSpacing(10)

        # Language
        self._lbl_lang = QLabel(tr("settings.language"))
        self._lbl_lang.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lang_combo = QComboBox()
        for code, key in self._LANGS:
            self.lang_combo.addItem(tr(key), code)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        fl.addRow(self._lbl_lang, self.lang_combo)

        # Default model
        self._lbl_model = QLabel(tr("settings.model"))
        self._lbl_model.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.model_edit = QComboBox()
        self.model_edit.setEditable(True)
        self.model_edit.addItems(self._MODELS)
        fl.addRow(self._lbl_model, self.model_edit)

        # Workspace
        self._lbl_ws = QLabel(tr("settings.workspace"))
        self._lbl_ws.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ws_row = QWidget()
        ws_h = QHBoxLayout(ws_row)
        ws_h.setContentsMargins(0, 0, 0, 0)
        ws_h.setSpacing(6)
        self.ws_edit = QLineEdit()
        self.ws_edit.setReadOnly(True)
        self.ws_edit.setStyleSheet("background:#f0f0f0; color:#555;")
        self.btn_ws_browse = QPushButton(tr("settings.ws_browse"))
        self.btn_ws_browse.setFixedWidth(100)
        self.btn_ws_browse.clicked.connect(self._on_browse_ws)
        ws_h.addWidget(self.ws_edit, stretch=1)
        ws_h.addWidget(self.btn_ws_browse)
        fl.addRow(self._lbl_ws, ws_row)

        root.addLayout(fl)
        root.addSpacing(16)

        # ── section: API Keys ─────────────────────────────────────────────────
        self._lbl_section_api = _section_label(tr("settings.section_api"))
        root.addWidget(self._lbl_section_api)
        root.addWidget(_sep())

        fl2 = QFormLayout()
        fl2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl2.setHorizontalSpacing(16)
        fl2.setVerticalSpacing(10)

        self._api_fields: dict[str, QLineEdit] = {}
        self._api_toggle_btns: dict[str, QPushButton] = {}

        for env_var, label_text in _API_KEYS:
            lbl = QLabel(label_text + ":")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row = QWidget()
            rh = QHBoxLayout(row)
            rh.setContentsMargins(0, 0, 0, 0)
            rh.setSpacing(6)
            field = QLineEdit()
            field.setEchoMode(QLineEdit.EchoMode.Password)
            field.setPlaceholderText(f"{env_var}=…")
            btn = QPushButton(tr("settings.api_show"))
            btn.setFixedWidth(64)
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, f=field, b=btn: self._toggle_visibility(f, b))
            rh.addWidget(field, stretch=1)
            rh.addWidget(btn)
            fl2.addRow(lbl, row)
            self._api_fields[env_var] = field
            self._api_toggle_btns[env_var] = btn

        root.addLayout(fl2)

        self._api_hint = QLabel(tr("settings.api_hint"))
        self._api_hint.setWordWrap(True)
        self._api_hint.setTextFormat(Qt.TextFormat.RichText)
        self._api_hint.setStyleSheet("color:#666; font-size:11px; margin-top:2px;")
        root.addWidget(self._api_hint)
        root.addSpacing(16)

        # ── save button + status ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton(tr("settings.save"))
        self.btn_save.setFixedHeight(34)
        self.btn_save.setFixedWidth(180)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#0063B1; color:white;"
            " border-radius:4px; padding:4px 20px; font-size:13px; }"
            "QPushButton:hover { background:#0078D4; }"
        )
        self.btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(self.btn_save)
        btn_row.addStretch()

        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("color:#27AE60; font-size:12px;")
        btn_row.addWidget(self.status_lbl)
        root.addLayout(btn_row)

        root.addSpacing(12)
        root.addWidget(_sep())

        # ── hint ──────────────────────────────────────────────────────────────
        self.hint_lbl = QLabel(tr("settings.hint"))
        self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setStyleSheet("color:#666; font-size:11px; margin-top:4px;")
        self.hint_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        root.addWidget(self.hint_lbl)

        root.addStretch()

    # ── values ────────────────────────────────────────────────────────────────

    def _load_values(self) -> None:
        # Language
        lang = settings.get("language", "pl")
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == lang:
                self.lang_combo.blockSignals(True)
                self.lang_combo.setCurrentIndex(i)
                self.lang_combo.blockSignals(False)
                break
        # Model
        model = settings.get("default_model", "gpt-4o")
        idx = self.model_edit.findText(model)
        if idx >= 0:
            self.model_edit.setCurrentIndex(idx)
        else:
            self.model_edit.setCurrentText(model)
        # Workspace
        from gui.state import get_workspace
        self.ws_edit.setText(str(get_workspace()))
        # API keys — read from file first, fall back to os.environ
        stored = _load_api_keys_file()
        for env_var, field in self._api_fields.items():
            value = stored.get(env_var) or os.environ.get(env_var, "")
            field.setText(value)

    def _toggle_visibility(self, field: QLineEdit, btn: QPushButton) -> None:
        if btn.isChecked():
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText(tr("settings.api_hide"))
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText(tr("settings.api_show"))

    def _on_lang_changed(self, index: int) -> None:
        lang = self.lang_combo.itemData(index)
        set_lang(lang)
        settings.put("language", lang)
        # Refresh lang combo labels (their display text was built at construction)
        for i in range(self.lang_combo.count()):
            code, key = self._LANGS[i]
            self.lang_combo.setItemText(i, tr(key))

    def _on_browse_ws(self) -> None:
        from gui.state import get_workspace, set_workspace
        d = QFileDialog.getExistingDirectory(
            self, tr("settings.workspace"), str(get_workspace())
        )
        if d:
            set_workspace(Path(d))
            self.ws_edit.setText(d)

    def _on_save(self) -> None:
        settings.put("default_model", self.model_edit.currentText().strip())
        settings.save()
        # Save API keys to file and apply to os.environ + litellm directly
        import litellm
        _LITELLM_ATTRS: dict[str, str] = {
            "OPENAI_API_KEY":    "openai_key",
            "ANTHROPIC_API_KEY": "anthropic_key",
            "GEMINI_API_KEY":    "gemini_key",
        }
        keys: dict[str, str] = {}
        for env_var, field in self._api_fields.items():
            value = field.text().strip()
            keys[env_var] = value
            if value:
                os.environ[env_var] = value
                if env_var in _LITELLM_ATTRS:
                    setattr(litellm, _LITELLM_ATTRS[env_var], value)
            else:
                if env_var in os.environ:
                    del os.environ[env_var]
                if env_var in _LITELLM_ATTRS:
                    setattr(litellm, _LITELLM_ATTRS[env_var], None)
        _save_api_keys_file(keys)
        self.status_lbl.setText(tr("settings.saved"))

    # ── retranslate ───────────────────────────────────────────────────────────

    def retranslate_ui(self) -> None:
        self._lbl_section_general.setText(tr("settings.section_general"))
        self._lbl_lang.setText(tr("settings.language"))
        self._lbl_model.setText(tr("settings.model"))
        self._lbl_ws.setText(tr("settings.workspace"))
        self.btn_ws_browse.setText(tr("settings.ws_browse"))
        self._lbl_section_api.setText(tr("settings.section_api"))
        self._api_hint.setText(tr("settings.api_hint"))
        for env_var, btn in self._api_toggle_btns.items():
            btn.setText(tr("settings.api_hide") if btn.isChecked() else tr("settings.api_show"))
        self.btn_save.setText(tr("settings.save"))
        self.hint_lbl.setText(tr("settings.hint"))
        if self.status_lbl.text():
            self.status_lbl.setText(tr("settings.saved"))
        # Refresh lang combo labels
        for i in range(self.lang_combo.count()):
            _, key = self._LANGS[i]
            self.lang_combo.setItemText(i, tr(key))
