"""Dialogs: ScanDialog, WorkspaceDialog."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QProgressBar,
    QPushButton, QTextEdit, QVBoxLayout,
)


class WorkspaceDialog(QDialog):
    """Pick a workspace (project root containing .github/)."""

    def __init__(self, current: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Zmień workspace")
        self.setMinimumWidth(500)
        self._chosen: Path | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Ścieżka do katalogu projektu (musi zawierać .github/):"))

        row = QHBoxLayout()
        self.path_edit = QLineEdit(str(current))
        btn_browse = QPushButton("Przeglądaj…")
        btn_browse.clicked.connect(self._browse)
        row.addWidget(self.path_edit)
        row.addWidget(btn_browse)
        layout.addLayout(row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Wybierz katalog projektu")
        if d:
            self.path_edit.setText(d)

    def _accept(self) -> None:
        p = Path(self.path_edit.text().strip())
        if not p.exists():
            QMessageBox.warning(self, "Błąd", f"Ścieżka nie istnieje: {p}")
            return
        self._chosen = p
        self.accept()

    def chosen_path(self) -> Path | None:
        return self._chosen


class ScanDialog(QDialog):
    """Preview and import files from a .github/ folder."""

    def __init__(self, source_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Skanuj .github/")
        self.setMinimumSize(600, 400)
        self._source = source_path

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Źródło: <b>{source_path}</b>"))

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Importuj wszystko")
        buttons.accepted.connect(self._import)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_preview()

    def _populate_preview(self) -> None:
        github_dir = self._source / ".github"
        if not github_dir.exists():
            self.preview.setPlainText("Brak folderu .github/ w wybranej ścieżce.")
            return

        lines = []
        self._items: list[tuple[str, Path]] = []
        for kind, subdir in [("agent", "agents"), ("skill", "skills"),
                              ("hook", "hooks"), ("instruction", "instructions")]:
            d = github_dir / subdir
            if d.exists():
                for p in sorted(d.glob("*.md")):
                    lines.append(f"[{kind}]  {p.name}")
                    self._items.append((kind, p))
        self.preview.setPlainText("\n".join(lines) if lines else "Brak plików .md do importu.")

    def _import(self) -> None:
        from storage.markdown_utils import (
            agent_from_markdown, skill_from_markdown,
            hook_from_markdown, instruction_from_markdown,
        )
        from core.agent import Agent
        from core.skill import Skill
        from core.hook import Hook
        from core.instruction import Instruction
        from gui.state import get_registry

        parsers = {
            "agent": (Agent, agent_from_markdown),
            "skill": (Skill, skill_from_markdown),
            "hook": (Hook, hook_from_markdown),
            "instruction": (Instruction, instruction_from_markdown),
        }
        store_attr = {
            "agent": "agents", "skill": "skills",
            "hook": "hooks", "instruction": "instructions",
        }

        reg = get_registry()
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self._items))

        errors = []
        for i, (kind, path) in enumerate(self._items):
            try:
                md = path.read_text(encoding="utf-8")
                model_cls, parser = parsers[kind]
                data = parser(md, path.stem)
                item = model_cls.model_validate(data)
                getattr(reg, store_attr[kind]).save(item)
            except Exception as exc:
                errors.append(f"{path.name}: {exc}")
            self.progress.setValue(i + 1)

        if errors:
            QMessageBox.warning(self, "Błędy", "\n".join(errors))
        else:
            QMessageBox.information(self, "Gotowe", f"Zaimportowano {len(self._items)} plików.")
        self.accept()
