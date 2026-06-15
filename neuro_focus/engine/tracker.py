"""Core CV + blink detection engine — no UI code."""

from __future__ import annotations

import os
import time
from collections import deque
from dataclasses import dataclass

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from neuro_focus.engine.calibration import EarCalibrator
from neuro_focus.engine.metrics import (
    attention_state,
    average_blink_duration,
    compute_bpm,
    fatigue_score_from_events,
    focus_score,
    is_fatigue_event,
    live_focus_estimate,
)

LEFT_EYE_IDX = [33, 133, 160, 144, 158, 153]
RIGHT_EYE_IDX = [362, 263, 385, 380, 387, 373]

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "face_landmarker.task",
)


@dataclass
class FrameState:
    ear: float
    blink_state: str
    bpm: float
    blink_count: int
    avg_blink_duration: float
    cognitive_state: str
    fatigue: float
    focus: float
    fatigue_events: int
    is_calibrated: bool
    calibration_progress: float
    face_detected: bool
    annotated_frame: np.ndarray | None = None

    def to_dict(self) -> dict:
        return {
            "ear": self.ear,
            "blink_state": self.blink_state,
            "bpm": self.bpm,
            "blink_count": self.blink_count,
            "avg_blink_duration": self.avg_blink_duration,
            "cognitive_state": self.cognitive_state,
            "fatigue": self.fatigue,
            "focus": self.focus,
            "fatigue_events": self.fatigue_events,
            "is_calibrated": self.is_calibrated,
            "calibration_progress": self.calibration_progress,
            "face_detected": self.face_detected,
        }


@dataclass
class TrackerConfig:
    frame_debounce_limit: int = 3
    baseline_bpm: float = 15.0
    bpm_window_seconds: float = 60.0
    calibration_duration: float = 7.0


class Tracker:
    """MediaPipe face tracking with EAR blink state machine."""

    def __init__(self, config: TrackerConfig | None = None) -> None:
        self.config = config or TrackerConfig()
        self._detector = self._create_detector()
        self._calibrator = EarCalibrator(duration_seconds=self.config.calibration_duration)
        self.session_started_at: float | None = None
        self.reset()

    @staticmethod
    def _create_detector() -> vision.FaceLandmarker:
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(
                f"Face landmarker model not found at {MODEL_PATH}. "
                "Download face_landmarker.task from MediaPipe and place it in neuro_focus/."
            )
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
        )
        return vision.FaceLandmarker.create_from_options(options)

    def reset(self) -> None:
        self.blink_counter = 0
        self.fatigue_event_count = 0
        self.frame_counter = 0
        self.current_blink_start = 0.0
        self.blink_durations: deque[float] = deque(maxlen=20)
        self.blink_times: deque[float] = deque()
        self.bpm_samples: list[float] = []
        self.ear_threshold = 0.24
        self.baseline_ear_mean = 0.0
        self.is_calibrated = False
        self.bpm = 0.0
        self.avg_blink_duration = 0.0
        self.session_started_at = time.perf_counter()
        self._calibrator.reset()
        self._calibrator.start()

    def session_elapsed_minutes(self) -> float:
        if self.session_started_at is None:
            return 0.0
        return (time.perf_counter() - self.session_started_at) / 60.0

    def session_elapsed_hours(self) -> float:
        return self.session_elapsed_minutes() / 60.0

    def final_focus_score(self) -> float:
        return focus_score(
            self.bpm_samples,
            self.fatigue_event_count,
            baseline_bpm=self.config.baseline_bpm,
        )

    @staticmethod
    def calculate_ear(eye_landmarks: list[int], img_w: int, img_h: int, face_landmarks) -> float:
        points = []
        for idx in eye_landmarks:
            pt = face_landmarks[idx]
            points.append(np.array([pt.x * img_w, pt.y * img_h]))

        v1 = np.linalg.norm(points[2] - points[3])
        v2 = np.linalg.norm(points[4] - points[5])
        h = np.linalg.norm(points[0] - points[1])
        if h == 0:
            return 0.0
        return (v1 + v2) / (2.0 * h)

    def _trim_blink_window(self) -> None:
        cutoff = time.perf_counter() - self.config.bpm_window_seconds
        while self.blink_times and self.blink_times[0] < cutoff:
            self.blink_times.popleft()

    def _process_blink_logic(self, avg_ear: float) -> str:
        blink_state = "open"

        if avg_ear < self.ear_threshold:
            if self.frame_counter == 0:
                self.current_blink_start = time.perf_counter()
            self.frame_counter += 1
            blink_state = "closed"
        else:
            if self.frame_counter >= self.config.frame_debounce_limit:
                self.blink_counter += 1
                blink_end = time.perf_counter()
                duration = blink_end - self.current_blink_start
                self.blink_durations.append(duration)
                self.avg_blink_duration = average_blink_duration(self.blink_durations)

                if is_fatigue_event(duration):
                    self.fatigue_event_count += 1

                self.blink_times.append(blink_end)
                self._trim_blink_window()
                self.bpm = compute_bpm(self.blink_times, self.config.bpm_window_seconds)
                if self.bpm > 0:
                    self.bpm_samples.append(self.bpm)

            self.frame_counter = 0

        return blink_state

    def get_frame_state(self, frame: np.ndarray, *, annotate: bool = True) -> FrameState:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self._detector.detect(mp_image)
        img_h, img_w = frame.shape[:2]

        ear = 0.0
        blink_state = "no_face"
        face_detected = False
        cognitive_state = "No Face Detected"
        calibration_progress = self._calibrator.progress

        if detection_result.face_landmarks:
            face_detected = True
            face_landmarks = detection_result.face_landmarks[0]
            left_ear = self.calculate_ear(LEFT_EYE_IDX, img_w, img_h, face_landmarks)
            right_ear = self.calculate_ear(RIGHT_EYE_IDX, img_w, img_h, face_landmarks)
            ear = (left_ear + right_ear) / 2.0

            if not self.is_calibrated:
                result = self._calibrator.add_sample(ear)
                if result is None and self._calibrator.seconds_remaining <= 0:
                    result = self._calibrator.force_complete()
                if result is not None:
                    self.ear_threshold = result.ear_threshold
                    self.baseline_ear_mean = result.baseline_ear_mean
                    self.is_calibrated = True
                cognitive_state = (
                    f"Calibrating... {self._calibrator.seconds_remaining:.1f}s left"
                )
                calibration_progress = self._calibrator.progress
            else:
                blink_state = self._process_blink_logic(ear)
                cognitive_state = attention_state(
                    bpm=self.bpm,
                    baseline_bpm=self.config.baseline_bpm,
                    avg_blink_duration=self.avg_blink_duration,
                    total_blinks=self.blink_counter,
                    fatigue_events=self.fatigue_event_count,
                    is_calibrated=True,
                )

        fatigue = fatigue_score_from_events(
            self.fatigue_event_count,
            max(self.session_elapsed_hours(), 1 / 60),
        )
        focus = (
            live_focus_estimate(
                self.bpm,
                self.fatigue_event_count,
                self.session_elapsed_minutes(),
                self.bpm_samples,
            )
            if self.is_calibrated
            else 0.0
        )

        annotated = frame.copy() if annotate else None
        if annotate and annotated is not None:
            self._draw_overlay(annotated, ear, cognitive_state, focus, fatigue)

        return FrameState(
            ear=ear,
            blink_state=blink_state,
            bpm=self.bpm,
            blink_count=self.blink_counter,
            avg_blink_duration=self.avg_blink_duration,
            cognitive_state=cognitive_state,
            fatigue=fatigue,
            focus=focus,
            fatigue_events=self.fatigue_event_count,
            is_calibrated=self.is_calibrated,
            calibration_progress=calibration_progress,
            face_detected=face_detected,
            annotated_frame=annotated,
        )

    def _draw_overlay(
        self,
        frame: np.ndarray,
        ear: float,
        state: str,
        focus: float,
        fatigue: float,
    ) -> None:
        color = (0, 255, 150) if self.is_calibrated else (0, 165, 255)
        cv2.putText(
            frame,
            f"Focus {focus:.0f}  Fatigue {fatigue:.0f}  BPM {self.bpm:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (240, 240, 240),
            2,
        )
        cv2.putText(
            frame,
            state[:48],
            (20, 72),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
        )
