"""Home dashboard — study OS landing page."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.session.analytics import (
    focus_insight,
    format_duration,
    greeting_name,
    last_session,
    recommended_block_minutes,
    study_streak_days,
    time_greeting,
    today_study_seconds,
)
from neuro_focus.session.session_manager import SessionManager
from neuro_focus.ui.widgets.stat_card import StatCard


class HomeView(QWidget):
    start_focus_requested = pyqtSignal()

    def __init__(self, session_manager: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self.session_manager = session_manager
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 36, 40, 24)
        layout.setSpacing(24)

        self.greeting = QLabel()
        self.greeting.setObjectName("appTitle")
        layout.addWidget(self.greeting)

        subtitle = QLabel("Your personal study operating system")
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)

        self.start_btn = QPushButton("Start Focus Session")
        self.start_btn.setObjectName("heroButton")
        self.start_btn.setFixedHeight(52)
        self.start_btn.clicked.connect(self.start_focus_requested.emit)
        layout.addWidget(self.start_btn)

        grid = QGridLayout()
        grid.setSpacing(14)
        self.today_card = StatCard("Today's Progress")
        self.streak_card = StatCard("Current Streak")
        self.last_card = StatCard("Last Session")
        self.block_card = StatCard("Recommended Block")
        grid.addWidget(self.today_card, 0, 0)
        grid.addWidget(self.streak_card, 0, 1)
        grid.addWidget(self.last_card, 1, 0)
        grid.addWidget(self.block_card, 1, 1)
        layout.addLayout(grid)

        insight_frame = QFrame()
        insight_frame.setObjectName("insightCard")
        insight_layout = QVBoxLayout(insight_frame)
        insight_layout.setContentsMargins(20, 18, 20, 18)
        insight_title = QLabel("Insight")
        insight_title.setObjectName("sectionTitle")
        self.insight_label = QLabel("")
        self.insight_label.setWordWrap(True)
        self.insight_label.setObjectName("muted")
        insight_layout.addWidget(insight_title)
        insight_layout.addWidget(self.insight_label)
        layout.addWidget(insight_frame)

        recent_title = QLabel("Recent Sessions")
        recent_title.setObjectName("sectionTitle")
        layout.addWidget(recent_title)
        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(8)
        layout.addLayout(self.recent_container)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def refresh(self) -> None:
        sessions = SessionManager.load_all_sessions()
        name = greeting_name("there")
        self.greeting.setText(f"{time_greeting()}, {name}")

        today_secs = today_study_seconds(sessions)
        self.today_card.set_value(format_duration(today_secs))
        self.streak_card.set_value(f"{study_streak_days(sessions)} days")

        recent = last_session(sessions)
        if recent:
            focus = float(recent.get("focus_score") or recent.get("focus") or 0)
            self.last_card.set_value(f"{recent.get('category', '—')}\n{focus:.0f} focus")
        else:
            self.last_card.set_value("—")

        block = recommended_block_minutes(sessions)
        self.block_card.set_value(f"{block} min")

        self.insight_label.setText(focus_insight(sessions))

        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for session in list(reversed(sessions))[:4]:
            row = QFrame()
            row.setObjectName("panel")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(16, 12, 16, 12)
            left = QLabel(
                f"{session.get('category', 'Session')}  ·  "
                f"{session.get('start_time', '')[:16]}"
            )
            right = QLabel(format_duration(float(session.get("duration_seconds") or 0)))
            right.setObjectName("muted")
            row_layout.addWidget(left)
            row_layout.addStretch()
            row_layout.addWidget(right)
            self.recent_container.addWidget(row)

        if not sessions:
            empty = QLabel("No sessions yet. Start your first focus block above.")
            empty.setObjectName("muted")
            self.recent_container.addWidget(empty)
