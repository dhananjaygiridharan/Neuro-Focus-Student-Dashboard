"""Camera preview that preserves aspect ratio — never stretches."""

from __future__ import annotations

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class AspectRatioCameraWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("cameraFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel("Camera inactive")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setObjectName("muted")
        self._label.setMinimumSize(640, 360)
        self._label.setScaledContents(False)
        layout.addWidget(self._label)
        self._last_pixmap: QPixmap | None = None

    def show_frame(self, frame: np.ndarray) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
        self._last_pixmap = QPixmap.fromImage(image)
        self._apply_scaled_pixmap()

    def set_placeholder(self, text: str) -> None:
        self._last_pixmap = None
        self._label.setText(text)
        self._label.setPixmap(QPixmap())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._last_pixmap is not None:
            self._apply_scaled_pixmap()

    def _apply_scaled_pixmap(self) -> None:
        if self._last_pixmap is None:
            return
        target = self._label.size()
        scaled = self._last_pixmap.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
