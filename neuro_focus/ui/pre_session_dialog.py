"""Pre-session questionnaire dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from neuro_focus.ui.styles import CATEGORY_OPTIONS, URGENCY_OPTIONS


class PreSessionDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Start Study Session")
        self.setMinimumWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QLabel("Before you begin")
        header.setObjectName("sectionTitle")
        subtitle = QLabel(
            "Tell Neuro-Focus what you're working on. This helps organize your session log."
        )
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(header)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(12)

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORY_OPTIONS)

        self.urgency_combo = QComboBox()
        self.urgency_combo.addItems(URGENCY_OPTIONS)
        self.urgency_combo.setCurrentText("Medium")

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("e.g. Chapter 7 biology notes")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Goals, context, or reminders for this session...")
        self.notes_input.setMaximumHeight(100)

        form.addRow("Study category", self.category_combo)
        form.addRow("Task urgency", self.urgency_combo)
        form.addRow("Task description", self.task_input)
        form.addRow("Session notes", self.notes_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Start Session")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setObjectName("primaryButton")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> dict[str, str]:
        return {
            "category": self.category_combo.currentText(),
            "urgency": self.urgency_combo.currentText(),
            "task_description": self.task_input.text().strip(),
            "pre_session_notes": self.notes_input.toPlainText().strip(),
        }
