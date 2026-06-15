"""Study session history log."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.session.analytics import format_duration
from neuro_focus.session.session_manager import SessionManager
from neuro_focus.ui.widgets.stat_card import StatCard


class SessionsView(QWidget):
    def __init__(self, session_manager: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self.session_manager = session_manager
        self._selected: dict | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(20)

        left = QFrame()
        left.setObjectName("panel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel("Sessions")
        title.setObjectName("sectionTitle")
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("ghostButton")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        left_layout.addLayout(header)

        subtitle = QLabel("Your structured study history")
        subtitle.setObjectName("muted")
        left_layout.addWidget(subtitle)

        self.session_list = QListWidget()
        self.session_list.currentItemChanged.connect(self._on_selected)
        left_layout.addWidget(self.session_list)
        root.addWidget(left, stretch=1)

        right = QFrame()
        right.setObjectName("panel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 20, 20, 20)

        self.detail_title = QLabel("Select a session")
        self.detail_title.setObjectName("sectionTitle")
        right_layout.addWidget(self.detail_title)

        self.meta_label = QLabel("")
        self.meta_label.setObjectName("muted")
        self.meta_label.setWordWrap(True)
        right_layout.addWidget(self.meta_label)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.duration_card = StatCard("Duration")
        self.focus_card = StatCard("Focus Score")
        self.blinks_card = StatCard("Blinks")
        self.bpm_card = StatCard("Avg BPM")
        self.events_card = StatCard("Fatigue Events")
        self.ear_card = StatCard("Avg EAR")
        grid.addWidget(self.duration_card, 0, 0)
        grid.addWidget(self.focus_card, 0, 1)
        grid.addWidget(self.blinks_card, 1, 0)
        grid.addWidget(self.bpm_card, 1, 1)
        grid.addWidget(self.events_card, 2, 0)
        grid.addWidget(self.ear_card, 2, 1)
        right_layout.addLayout(grid)
        right_layout.addStretch()
        root.addWidget(right, stretch=2)

    def refresh(self) -> None:
        sessions = SessionManager.load_all_sessions()
        sessions = list(reversed(sessions))
        self.session_list.clear()

        if not sessions:
            item = QListWidgetItem("No sessions yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.session_list.addItem(item)
            return

        for session in sessions:
            label = (
                f"{session.get('category', 'Session')}  ·  "
                f"{session.get('urgency', '')}  ·  "
                f"{session.get('start_time', '')[:16]}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, session)
            self.session_list.addItem(item)
        self.session_list.setCurrentRow(0)

    def _on_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        session = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(session, dict):
            return

        self._selected = session
        self.detail_title.setText(session.get("task_description") or session.get("category", "Session"))
        self.meta_label.setText(
            f"{session.get('category')} · {session.get('urgency')} urgency\n"
            f"{session.get('start_time')} → {session.get('end_time') or '—'}"
        )

        duration = float(session.get("duration_seconds") or 0)
        self.duration_card.set_value(format_duration(duration))
        self.focus_card.set_value(f"{float(session.get('focus_score') or 0):.0f}")
        self.blinks_card.set_value(str(session.get("total_blinks", "0")))
        self.bpm_card.set_value(f"{float(session.get('avg_bpm') or 0):.1f}")
        self.events_card.set_value(str(session.get("fatigue_events") or 0))
        self.ear_card.set_value(f"{float(session.get('avg_ear') or 0):.3f}")
