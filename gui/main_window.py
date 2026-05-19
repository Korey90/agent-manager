"""Main window."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QFileDialog, QLabel, QMainWindow,
    QStatusBar, QTabWidget, QToolBar, QWidget,
)

from gui.panels import AgentPanel, HookPanel, InstructionPanel, SkillPanel, ValidationPanel
from gui.diagram import DiagramPanel
from gui.run_panel import RunPanel
from gui.export_panel import ExportPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Agent Manager")
        self.resize(1100, 720)
        self._build_menu()
        self._build_toolbar()
        self._build_tabs()
        self._build_statusbar()
        self._update_status()

    # ── menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("Plik")
        act_ws = QAction("Zmień workspace…", self)
        act_ws.setShortcut("Ctrl+Shift+O")
        act_ws.triggered.connect(self._change_workspace)
        file_menu.addAction(act_ws)

        act_scan = QAction("Skanuj .github/…", self)
        act_scan.setShortcut("Ctrl+I")
        act_scan.triggered.connect(self._scan)
        file_menu.addAction(act_scan)

        file_menu.addSeparator()
        act_quit = QAction("Zamknij", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

    # ── toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        tb = QToolBar("Główny pasek")
        tb.setMovable(False)
        self.addToolBar(tb)

        act_ws = QAction("📂 Workspace", self)
        act_ws.setToolTip("Zmień folder projektu (Ctrl+Shift+O)")
        act_ws.triggered.connect(self._change_workspace)
        tb.addAction(act_ws)

        act_scan = QAction("⬇ Skanuj .github/", self)
        act_scan.setToolTip("Importuj agentów/skille/hooki z innego projektu (Ctrl+I)")
        act_scan.triggered.connect(self._scan)
        tb.addAction(act_scan)

        tb.addSeparator()

        act_refresh = QAction("↺ Odśwież", self)
        act_refresh.setShortcut("F5")
        act_refresh.triggered.connect(self._refresh_current_tab)
        tb.addAction(act_refresh)

    # ── tabs ──────────────────────────────────────────────────────────────────

    def _build_tabs(self) -> None:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.agent_panel = AgentPanel()
        self.skill_panel = SkillPanel()
        self.hook_panel = HookPanel()
        self.instr_panel = InstructionPanel()
        self.diag_panel  = DiagramPanel()
        self.valid_panel = ValidationPanel()
        self.valid_panel.navigate_to.connect(self._on_navigate)
        self.run_panel   = RunPanel()
        self.export_panel = ExportPanel()

        self.tabs.addTab(self.agent_panel,   "🤖  Agenci")
        self.tabs.addTab(self.skill_panel,   "⚡  Skille")
        self.tabs.addTab(self.hook_panel,    "🔗  Hooki")
        self.tabs.addTab(self.instr_panel,   "📋  Instrukcje")
        self.tabs.addTab(self.diag_panel,    "🗺  Diagram")
        self.tabs.addTab(self.valid_panel,   "✅  Walidacja")
        self.tabs.addTab(self.run_panel,     "▶  Uruchom")
        self.tabs.addTab(self.export_panel,  "📤  Eksport")

    # ── status bar ────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:
        self.status_label = QLabel()
        sb = QStatusBar()
        sb.addPermanentWidget(self.status_label)
        self.setStatusBar(sb)

    def _update_status(self) -> None:
        from gui.state import get_workspace
        ws = get_workspace()
        self.status_label.setText(f"Workspace: {ws}")
        self.setWindowTitle(f"Agent Manager — {ws.name}")

    # ── actions ───────────────────────────────────────────────────────────────

    def _change_workspace(self) -> None:
        from gui.state import get_workspace, set_workspace
        from gui.dialogs import WorkspaceDialog
        dlg = WorkspaceDialog(get_workspace(), self)
        if dlg.exec() and dlg.chosen_path():
            set_workspace(dlg.chosen_path())
            self._refresh_all()
            self._update_status()

    def _scan(self) -> None:
        from gui.dialogs import ScanDialog
        d = QFileDialog.getExistingDirectory(self, "Wybierz projekt do skanowania")
        if not d:
            return
        dlg = ScanDialog(Path(d), self)
        if dlg.exec():
            self._refresh_all()

    def _refresh_all(self) -> None:
        for panel in (self.agent_panel, self.skill_panel,
                      self.hook_panel, self.instr_panel,
                      self.diag_panel):
            panel.refresh()

    def _refresh_current_tab(self) -> None:
        widget = self.tabs.currentWidget()
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _on_navigate(self, kind: str, item_id: str) -> None:
        """Switch to the correct panel and select + flash the item."""
        panel_map = {
            "agent": self.agent_panel,
            "skill": self.skill_panel,
            "hook":  self.hook_panel,
        }
        panel = panel_map.get(kind)
        if not panel:
            return
        self.tabs.setCurrentWidget(panel)
        panel.select_by_id(item_id)
