#!/usr/bin/env python
"""Agent Manager — GUI entry point."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

import gui.state as state
from gui.main_window import MainWindow


STYLESHEET = """
QMainWindow { background: #f5f5f5; }

QTabWidget::pane { border: 1px solid #ccc; }
QTabBar::tab {
    padding: 8px 18px;
    background: #e0e0e0;
    border: 1px solid #ccc;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
}
QTabBar::tab:selected { background: white; font-weight: bold; }
QTabBar::tab:hover:!selected { background: #ebebeb; }

QListWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background: white;
    outline: none;
}
QListWidget::item { padding: 5px 8px; }
QListWidget::item:selected { background: #0063B1; color: white; }
QListWidget::item:hover:!selected { background: #e8f0fe; }

QLineEdit, QPlainTextEdit {
    border: 1px solid #ccc;
    border-radius: 3px;
    padding: 3px 6px;
    background: white;
}
QLineEdit:focus, QPlainTextEdit:focus { border-color: #0063B1; }
QLineEdit[readOnly="true"] { background: #f0f0f0; color: #666; }

QPushButton {
    padding: 4px 12px;
    border: 1px solid #bbb;
    border-radius: 3px;
    background: #fdfdfd;
}
QPushButton:hover { background: #e8e8e8; }
QPushButton:pressed { background: #d0d0d0; }

QFormLayout { spacing: 8px; }
QScrollArea { border: none; }
QToolBar { background: #f0f0f0; border-bottom: 1px solid #ddd; spacing: 4px; }
QStatusBar { background: #e8e8e8; }
"""


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Agent Manager")
    app.setStyleSheet(STYLESHEET)

    # Set default workspace from config
    from config import GITHUB_DIR
    state.set_workspace(GITHUB_DIR.parent)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
