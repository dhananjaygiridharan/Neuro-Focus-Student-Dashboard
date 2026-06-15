"""App settings."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.session.session_manager import SessionManager


class SettingsView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 24)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        subtitle = QLabel("Personalize your study OS")
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(14)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your first name")

        self.nudge_checkbox = QCheckBox("Show fatigue break reminders")
        self.nudge_checkbox.setChecked(True)

        form.addRow("Display name", self.name_input)
        form.addRow("Notifications", self.nudge_checkbox)
        layout.addLayout(form)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

        about = QLabel(
            "Neuro-Focus uses computer vision biomarkers (blink rate, duration) "
            "as behavioral signals — not clinical diagnostics."
        )
        about.setWordWrap(True)
        about.setObjectName("muted")
        layout.addWidget(about)
        layout.addStretch()

    def _load(self) -> None:
        settings = SessionManager.load_settings()
        self.name_input.setText(settings.get("display_name", ""))
        self.nudge_checkbox.setChecked(settings.get("fatigue_nudges", True))

    def _save(self) -> None:
        SessionManager.save_settings(
            {
                "display_name": self.name_input.text().strip(),
                "fatigue_nudges": self.nudge_checkbox.isChecked(),
            }
        )
