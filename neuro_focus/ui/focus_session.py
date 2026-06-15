"""Live focus session — calibration then tracking (camera only here)."""

from __future__ import annotations

import time

import cv2
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.engine.tracker import FrameState, Tracker
from neuro_focus.session.session_manager import SessionManager
from neuro_focus.ui.styles import STATUS_COLORS
from neuro_focus.ui.widgets.camera_widget import AspectRatioCameraWidget
from neuro_focus.ui.widgets.stat_card import StatCard


class FocusSessionView(QWidget):
    session_ended = pyqtSignal(object)
    back_requested = pyqtSignal()

    FATIGUE_NUDGE_SECONDS = 240

    def __init__(
        self,
        tracker: Tracker,
        session_manager: SessionManager,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.tracker = tracker
        self.session_manager = session_manager
        self._cap: cv2.VideoCapture | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_frame)
        self._elapsed_seconds = 0.0
        self._last_state: FrameState | None = None
        self._fatigue_since: float | None = None
        self._nudge_shown = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(16)

        header = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghostButton")
        back_btn.clicked.connect(self._on_back)
        self.page_title = QLabel("Focus Session")
        self.page_title.setObjectName("sectionTitle")
        self.status_dot = QLabel("● Ready")
        self.status_dot.setStyleSheet(f"color: {STATUS_COLORS['idle']}; font-weight: 600;")
        header.addWidget(back_btn)
        header.addWidget(self.page_title)
        header.addStretch()
        header.addWidget(self.status_dot)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(20)

        left = QVBoxLayout()
        self.camera = AspectRatioCameraWidget()
        left.addWidget(self.camera, stretch=1)

        self.calibration_bar = QProgressBar()
        self.calibration_bar.setRange(0, 100)
        self.calibration_bar.setVisible(False)
        self.calibration_label = QLabel("")
        self.calibration_label.setObjectName("muted")
        self.calibration_label.setVisible(False)
        left.addWidget(self.calibration_bar)
        left.addWidget(self.calibration_label)
        body.addLayout(left, stretch=3)

        right_panel = QFrame()
        right_panel.setObjectName("panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(14)

        self.session_info = QLabel("")
        self.session_info.setWordWrap(True)
        self.session_info.setObjectName("muted")
        right_layout.addWidget(self.session_info)

        self.elapsed_label = QLabel("Elapsed: 00:00:00")
        self.elapsed_label.setObjectName("muted")
        right_layout.addWidget(self.elapsed_label)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.focus_card = StatCard("Focus Score")
        self.fatigue_card = StatCard("Fatigue")
        self.bpm_card = StatCard("BPM")
        self.blink_card = StatCard("Blinks")
        self.events_card = StatCard("Fatigue Events")
        self.state_card = StatCard("State")
        grid.addWidget(self.focus_card, 0, 0)
        grid.addWidget(self.fatigue_card, 0, 1)
        grid.addWidget(self.bpm_card, 1, 0)
        grid.addWidget(self.blink_card, 1, 1)
        grid.addWidget(self.events_card, 2, 0)
        grid.addWidget(self.state_card, 2, 1)
        right_layout.addLayout(grid)

        self.end_btn = QPushButton("End Session")
        self.end_btn.setObjectName("dangerButton")
        self.end_btn.clicked.connect(self.end_session)
        right_layout.addWidget(self.end_btn)

        self.nudge_banner = QFrame()
        self.nudge_banner.setObjectName("nudgeBanner")
        self.nudge_banner.setVisible(False)
        nudge_layout = QVBoxLayout(self.nudge_banner)
        nudge_layout.setContentsMargins(14, 12, 14, 12)
        nudge_title = QLabel("Fatigue detected")
        nudge_title.setObjectName("sectionTitle")
        nudge_body = QLabel("Consider water, a short walk, or a 20-second eye rest.")
        nudge_body.setWordWrap(True)
        nudge_body.setObjectName("muted")
        nudge_layout.addWidget(nudge_title)
        nudge_layout.addWidget(nudge_body)
        right_layout.addWidget(self.nudge_banner)
        right_layout.addStretch()
        body.addWidget(right_panel, stretch=1)
        root.addLayout(body, stretch=1)

    def begin_session(self, session) -> None:
        self.tracker.reset()
        self._elapsed_seconds = 0.0
        self._fatigue_since = None
        self._nudge_shown = False
        self.nudge_banner.setVisible(False)
        self.session_info.setText(
            f"{session.category} · {session.urgency} urgency\n"
            f"{session.task_description or 'No description'}"
        )
        self._set_status("calibrating", "● Calibrating")
        self.start_camera()

    def start_camera(self) -> None:
        if self._cap is not None:
            return
        self._cap = cv2.VideoCapture(0)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.camera.set_placeholder("")
        self._timer.start(33)

    def stop_camera(self) -> None:
        self._timer.stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self.camera.set_placeholder("Camera inactive")

    def end_session(self) -> None:
        final = self._last_state.to_dict() if self._last_state else {}
        final["focus_score"] = self.tracker.final_focus_score()
        finished = self.session_manager.end_session(final)
        self.stop_camera()
        self._set_status("idle", "● Complete")
        if finished:
            self.session_ended.emit(finished)

    def _on_back(self) -> None:
        if self.session_manager.is_active:
            self.end_session()
        else:
            self.stop_camera()
            self.back_requested.emit()

    def _set_status(self, key: str, text: str) -> None:
        color = STATUS_COLORS.get(key, STATUS_COLORS["idle"])
        self.status_dot.setText(text)
        self.status_dot.setStyleSheet(f"color: {color}; font-weight: 600;")

    def _on_frame(self) -> None:
        if self._cap is None or not self._cap.isOpened():
            return

        success, frame = self._cap.read()
        if not success:
            return

        frame = cv2.flip(frame, 1)
        state = self.tracker.get_frame_state(frame, annotate=True)
        self._last_state = state
        display = state.annotated_frame if state.annotated_frame is not None else frame
        self.camera.show_frame(display)
        self._update_metrics(state)

        if self.session_manager.is_active:
            self._elapsed_seconds += 1 / 30.0
            h, rem = divmod(int(self._elapsed_seconds), 3600)
            m, s = divmod(rem, 60)
            self.elapsed_label.setText(f"Elapsed: {h:02d}:{m:02d}:{s:02d}")
            self.session_manager.log_frame_state(state.to_dict())
            self._check_fatigue_nudge(state)

    def _check_fatigue_nudge(self, state: FrameState) -> None:
        settings = SessionManager.load_settings()
        if not settings.get("fatigue_nudges", True) or self._nudge_shown:
            return

        fatigued = state.fatigue >= 35 or state.fatigue_events >= 2
        now = time.perf_counter()
        if fatigued:
            if self._fatigue_since is None:
                self._fatigue_since = now
            elif now - self._fatigue_since >= self.FATIGUE_NUDGE_SECONDS:
                self.nudge_banner.setVisible(True)
                self._nudge_shown = True
        else:
            self._fatigue_since = None

    def _update_metrics(self, state: FrameState) -> None:
        self.focus_card.set_value(f"{state.focus:.0f}")
        self.fatigue_card.set_value(f"{state.fatigue:.0f}")
        self.bpm_card.set_value(f"{state.bpm:.1f}")
        self.blink_card.set_value(str(state.blink_count))
        self.events_card.set_value(str(state.fatigue_events))
        short = state.cognitive_state[:16] + "…" if len(state.cognitive_state) > 16 else state.cognitive_state
        self.state_card.set_value(short if state.face_detected else "—")

        if not self.session_manager.is_active:
            return

        if not state.face_detected:
            self._set_status("no_face", "● No Face")
        elif not state.is_calibrated:
            self._set_status("calibrating", "● Calibrating")
            self.calibration_bar.setVisible(True)
            self.calibration_label.setVisible(True)
            self.calibration_bar.setValue(int(state.calibration_progress * 100))
            self.calibration_label.setText(state.cognitive_state)
        else:
            self._set_status("tracking", "● Tracking")
            self.calibration_bar.setVisible(False)
            self.calibration_label.setVisible(False)
