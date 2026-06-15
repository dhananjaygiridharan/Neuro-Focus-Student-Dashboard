"""Application shell — home-first with bottom navigation."""

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from neuro_focus.engine.tracker import Tracker
from neuro_focus.session.session_manager import SessionManager
from neuro_focus.ui.analytics_view import AnalyticsView
from neuro_focus.ui.focus_session import FocusSessionView
from neuro_focus.ui.home_view import HomeView
from neuro_focus.ui.journal_view import JournalView
from neuro_focus.ui.post_session_dialog import PostSessionDialog
from neuro_focus.ui.pre_session_dialog import PreSessionDialog
from neuro_focus.ui.sessions_view import SessionsView
from neuro_focus.ui.settings_view import SettingsView
from neuro_focus.ui.styles import APP_STYLESHEET
from neuro_focus.ui.widgets.bottom_nav import BottomNavBar

PAGE_HOME = 0
PAGE_SESSIONS = 1
PAGE_ANALYTICS = 2
PAGE_JOURNAL = 3
PAGE_SETTINGS = 4
PAGE_FOCUS = 5


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Neuro-Focus")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 820)

        self.tracker = Tracker()
        self.session_manager = SessionManager(log_interval_seconds=3.0)

        self._build_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self.show_page(PAGE_HOME)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.home = HomeView(self.session_manager)
        self.sessions = SessionsView(self.session_manager)
        self.analytics = AnalyticsView()
        self.journal = JournalView(self.session_manager)
        self.settings = SettingsView()
        self.focus = FocusSessionView(self.tracker, self.session_manager)

        for page in (self.home, self.sessions, self.analytics, self.journal, self.settings, self.focus):
            self.stack.addWidget(page)

        self.home.start_focus_requested.connect(self._start_focus_flow)
        self.focus.session_ended.connect(self._on_session_ended)
        self.focus.back_requested.connect(lambda: self.show_page(PAGE_HOME))

        layout.addWidget(self.stack, stretch=1)

        self.bottom_nav = BottomNavBar()
        self.bottom_nav.page_selected.connect(self._on_nav)
        layout.addWidget(self.bottom_nav)

    def show_page(self, index: int) -> None:
        if index != PAGE_FOCUS and self.session_manager.is_active:
            return
        if index == PAGE_HOME:
            self.home.refresh()
        elif index == PAGE_SESSIONS:
            self.sessions.refresh()
        elif index == PAGE_ANALYTICS:
            self.analytics.refresh()
        elif index == PAGE_JOURNAL:
            self.journal.refresh()

        if index < 5:
            self.bottom_nav.set_active(index)
        self.stack.setCurrentIndex(index)

    def _on_nav(self, index: int) -> None:
        if self.session_manager.is_active:
            return
        self.show_page(index)

    def _start_focus_flow(self) -> None:
        dialog = PreSessionDialog(self)
        if dialog.exec() != PreSessionDialog.DialogCode.Accepted:
            return

        values = dialog.get_values()
        session = self.session_manager.start_session(
            category=values["category"],
            urgency=values["urgency"],
            task_description=values["task_description"],
            pre_session_notes=values["pre_session_notes"],
        )
        self.focus.begin_session(session)
        self.stack.setCurrentIndex(PAGE_FOCUS)

    def _on_session_ended(self, finished) -> None:
        dialog = PostSessionDialog(category=finished.category, parent=self)
        if dialog.exec() == PostSessionDialog.DialogCode.Accepted:
            SessionManager.save_journal_entry(finished.session_id, dialog.get_values())

        self.show_page(PAGE_HOME)

    def closeEvent(self, event) -> None:
        if self.session_manager.is_active:
            self.focus.end_session()
        else:
            self.focus.stop_camera()
        super().closeEvent(event)
