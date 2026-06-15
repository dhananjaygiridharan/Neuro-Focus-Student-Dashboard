"""Weekly analytics dashboard."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.session.analytics import format_duration, weekly_summary
from neuro_focus.session.session_manager import SessionManager
from neuro_focus.ui.widgets.stat_card import StatCard


class AnalyticsView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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
        layout.setSpacing(20)

        title = QLabel("Analytics")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        subtitle = QLabel("Weekly behavioral trends from your study sessions")
        subtitle.setObjectName("muted")
        layout.addWidget(subtitle)

        self.grid = QGridLayout()
        self.grid.setSpacing(14)
        self.hours_card = StatCard("Total Hours (7d)")
        self.count_card = StatCard("Sessions (7d)")
        self.focus_card = StatCard("Avg Focus")
        self.events_card = StatCard("Fatigue Events")
        self.bpm_card = StatCard("Avg BPM")
        self.blink_card = StatCard("Avg Blink Duration")
        self.best_card = StatCard("Best Subject")
        self.worst_card = StatCard("Needs Work")
        cards = [
            self.hours_card,
            self.count_card,
            self.focus_card,
            self.events_card,
            self.bpm_card,
            self.blink_card,
            self.best_card,
            self.worst_card,
        ]
        for i, card in enumerate(cards):
            self.grid.addWidget(card, i // 2, i % 2)
        layout.addLayout(self.grid)

        self.trend_label = QFrame()
        self.trend_label.setObjectName("insightCard")
        trend_layout = QVBoxLayout(self.trend_label)
        trend_layout.setContentsMargins(20, 18, 20, 18)
        trend_title = QLabel("Weekly Summary")
        trend_title.setObjectName("sectionTitle")
        self.summary_text = QLabel("")
        self.summary_text.setWordWrap(True)
        self.summary_text.setObjectName("muted")
        trend_layout.addWidget(trend_title)
        trend_layout.addWidget(self.summary_text)
        layout.addWidget(self.trend_label)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def refresh(self) -> None:
        sessions = SessionManager.load_all_sessions()
        summary = weekly_summary(sessions)

        self.hours_card.set_value(f"{summary['total_hours']:.1f}h")
        self.count_card.set_value(str(summary["session_count"]))
        self.focus_card.set_value(f"{summary['avg_focus']:.0f}")
        self.events_card.set_value(str(summary["total_fatigue_events"]))
        self.bpm_card.set_value(f"{summary['avg_bpm']:.1f}")
        blink = summary.get("avg_blink_duration", 0)
        self.blink_card.set_value(f"{blink:.2f}s" if blink else "—")
        self.best_card.set_value(str(summary["best_subject"])[:14])
        self.worst_card.set_value(str(summary["worst_subject"])[:14])

        total_secs = summary["total_hours"] * 3600
        self.summary_text.setText(
            f"You logged {summary['session_count']} sessions totaling "
            f"{format_duration(total_secs)} this week. "
            f"Average focus score: {summary['avg_focus']:.0f}. "
            f"Strongest category: {summary['best_subject']}."
        )
