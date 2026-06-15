"""Post-session journal prompts."""

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

from neuro_focus.ui.styles import FOCUS_RATING_OPTIONS


class PostSessionDialog(QDialog):
    def __init__(self, category: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Session Reflection")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QLabel("How did it go?")
        header.setObjectName("sectionTitle")
        subtitle = QLabel("A quick reflection helps Neuro-Focus learn your study patterns.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(header)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(12)

        self.what_input = QLineEdit()
        self.what_input.setPlaceholderText("What did you work on?")
        if category:
            self.what_input.setText(category)

        self.focus_combo = QComboBox()
        self.focus_combo.addItems(FOCUS_RATING_OPTIONS)
        self.focus_combo.setCurrentIndex(2)

        self.distraction_input = QTextEdit()
        self.distraction_input.setPlaceholderText("What distracted you, if anything?")
        self.distraction_input.setMaximumHeight(80)

        self.reflection_input = QTextEdit()
        self.reflection_input.setPlaceholderText("What worked? What would you change next time?")
        self.reflection_input.setMaximumHeight(100)

        form.addRow("What did you study?", self.what_input)
        form.addRow("How focused did you feel?", self.focus_combo)
        form.addRow("Distractions", self.distraction_input)
        form.addRow("Reflection", self.reflection_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Skip")
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Save Journal")
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primaryButton")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> dict[str, str]:
        return {
            "what_studied": self.what_input.text().strip(),
            "focus_rating": self.focus_combo.currentText(),
            "distractions": self.distraction_input.toPlainText().strip(),
            "reflection": self.reflection_input.toPlainText().strip(),
        }
