"""Main window."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QFileDialog, QLabel, QMainWindow, QMessageBox,
    QStatusBar, QTabWidget, QToolBar, QWidget,
)

from gui.panels import AgentPanel, HookPanel, InstructionPanel, SkillPanel, ValidationPanel
from gui.diagram import DiagramPanel
from gui.run_panel import RunPanel
from gui.export_panel import ExportPanel
from gui.settings_panel import SettingsPanel
from gui.i18n import tr, lang_signals


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

        self._menu_file = mb.addMenu(tr("menu.file"))
        self._act_ws = QAction(tr("action.change_workspace"), self)
        self._act_ws.setShortcut("Ctrl+Shift+O")
        self._act_ws.triggered.connect(self._change_workspace)
        self._menu_file.addAction(self._act_ws)

        self._act_scan = QAction(tr("action.scan"), self)
        self._act_scan.setShortcut("Ctrl+I")
        self._act_scan.triggered.connect(self._scan)
        self._menu_file.addAction(self._act_scan)

        self._menu_file.addSeparator()
        self._act_quit = QAction(tr("action.quit"), self)
        self._act_quit.setShortcut("Ctrl+Q")
        self._act_quit.triggered.connect(self.close)
        self._menu_file.addAction(self._act_quit)

        self._menu_help = mb.addMenu(tr("menu.help"))
        self._act_about = QAction(tr("action.about"), self)
        self._act_about.setShortcut("F1")
        self._act_about.triggered.connect(self._show_about)
        self._menu_help.addAction(self._act_about)

    # ── toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        self._toolbar = QToolBar("main")
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)

        self._tb_act_ws = QAction(tr("toolbar.workspace"), self)
        self._tb_act_ws.setToolTip("Ctrl+Shift+O")
        self._tb_act_ws.triggered.connect(self._change_workspace)
        self._toolbar.addAction(self._tb_act_ws)

        self._tb_act_scan = QAction(tr("toolbar.scan"), self)
        self._tb_act_scan.setToolTip("Ctrl+I")
        self._tb_act_scan.triggered.connect(self._scan)
        self._toolbar.addAction(self._tb_act_scan)

        self._toolbar.addSeparator()

        self._tb_act_refresh = QAction(tr("toolbar.refresh"), self)
        self._tb_act_refresh.setShortcut("F5")
        self._tb_act_refresh.triggered.connect(self._refresh_current_tab)
        self._toolbar.addAction(self._tb_act_refresh)

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
        self.run_panel    = RunPanel()
        self.export_panel = ExportPanel()
        self.settings_panel = SettingsPanel()

        self.tabs.addTab(self.agent_panel,    tr("tab.agents"))
        self.tabs.addTab(self.skill_panel,    tr("tab.skills"))
        self.tabs.addTab(self.hook_panel,     tr("tab.hooks"))
        self.tabs.addTab(self.instr_panel,    tr("tab.instructions"))
        self.tabs.addTab(self.diag_panel,     tr("tab.diagram"))
        self.tabs.addTab(self.valid_panel,    tr("tab.validation"))
        self.tabs.addTab(self.run_panel,      tr("tab.run"))
        self.tabs.addTab(self.export_panel,   tr("tab.export"))
        self.tabs.addTab(self.settings_panel, tr("tab.settings"))

        lang_signals().changed.connect(self._retranslate_ui)

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

    def _retranslate_ui(self) -> None:
        """Update all translatable strings after language change."""
        _tab_keys = [
            "tab.agents", "tab.skills", "tab.hooks", "tab.instructions",
            "tab.diagram", "tab.validation", "tab.run", "tab.export", "tab.settings",
        ]
        for i, key in enumerate(_tab_keys):
            self.tabs.setTabText(i, tr(key))
        # Menu
        self._menu_file.setTitle(tr("menu.file"))
        self._menu_help.setTitle(tr("menu.help"))
        self._act_ws.setText(tr("action.change_workspace"))
        self._act_scan.setText(tr("action.scan"))
        self._act_quit.setText(tr("action.quit"))
        self._act_about.setText(tr("action.about"))
        # Toolbar
        self._tb_act_ws.setText(tr("toolbar.workspace"))
        self._tb_act_scan.setText(tr("toolbar.scan"))
        self._tb_act_refresh.setText(tr("toolbar.refresh"))
        # Panels
        for panel in (
            self.agent_panel, self.skill_panel, self.hook_panel,
            self.instr_panel, self.valid_panel, self.run_panel,
            self.export_panel,
        ):
            if hasattr(panel, "retranslate_ui"):
                panel.retranslate_ui()

    def _show_about(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle(tr("about.title"))
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(tr("about.body"))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

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
