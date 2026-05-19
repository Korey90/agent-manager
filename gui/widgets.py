"""Reusable Qt widgets."""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QInputDialog, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QPlainTextEdit,
    QSizePolicy, QVBoxLayout, QWidget,
)


class ListEditor(QWidget):
    """Editable list of strings — add / edit (double-click) / remove."""

    changed = pyqtSignal()

    def __init__(self, placeholder: str = "New item…", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._placeholder = placeholder
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setMinimumHeight(80)
        self.list_widget.itemDoubleClicked.connect(self._edit_item)
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("＋ Dodaj")
        self.btn_edit = QPushButton("✎ Edytuj")
        self.btn_del = QPushButton("✕ Usuń")
        for btn in (self.btn_add, self.btn_edit, self.btn_del):
            btn.setFixedHeight(22)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.btn_add.clicked.connect(self._add_item)
        self.btn_edit.clicked.connect(self._edit_selected)
        self.btn_del.clicked.connect(self._remove_item)

    # ── actions ───────────────────────────────────────────────────────────────

    def _add_item(self) -> None:
        text, ok = QInputDialog.getText(self, "Dodaj", self._placeholder)
        if ok and text.strip():
            self.list_widget.addItem(text.strip())
            self.changed.emit()

    def _edit_item(self, item: QListWidgetItem) -> None:
        text, ok = QInputDialog.getText(self, "Edytuj", self._placeholder, text=item.text())
        if ok and text.strip():
            item.setText(text.strip())
            self.changed.emit()

    def _edit_selected(self) -> None:
        item = self.list_widget.currentItem()
        if item:
            self._edit_item(item)

    def _remove_item(self) -> None:
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.takeItem(row)
            self.changed.emit()

    # ── data access ───────────────────────────────────────────────────────────

    def get_items(self) -> list[str]:
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

    def set_items(self, items: list[str]) -> None:
        self.list_widget.clear()
        for it in items:
            self.list_widget.addItem(it)


class CodeEditor(QPlainTextEdit):
    """Monospace plain-text editor for templates / markdown."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setMinimumHeight(120)
