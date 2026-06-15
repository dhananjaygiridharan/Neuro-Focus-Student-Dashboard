"""EAR calibration with noise-filtered stable open-eye sampling."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


@dataclass
class CalibrationResult:
    ear_threshold: float
    baseline_ear_mean: float
    sample_count: int


class EarCalibrator:
    """Collect stable open-eye EAR samples and derive a blink threshold."""

    def __init__(
        self,
        duration_seconds: float = 7.0,
        open_eye_ratio: float = 0.8,
        threshold_multiplier: float = 0.75,
        trim_percent: float = 0.10,
    ) -> None:
        self.duration_seconds = duration_seconds
        self.open_eye_ratio = open_eye_ratio
        self.threshold_multiplier = threshold_multiplier
        self.trim_percent = trim_percent
        self._samples: list[float] = []
        self._started_at: float | None = None
        self._finished = False
        self._result: CalibrationResult | None = None

    @property
    def is_complete(self) -> bool:
        return self._finished

    @property
    def result(self) -> CalibrationResult | None:
        return self._result

    @property
    def progress(self) -> float:
        if self._started_at is None:
            return 0.0
        elapsed = time.perf_counter() - self._started_at
        return min(1.0, elapsed / self.duration_seconds)

    @property
    def seconds_remaining(self) -> float:
        if self._started_at is None:
            return self.duration_seconds
        elapsed = time.perf_counter() - self._started_at
        return max(0.0, self.duration_seconds - elapsed)

    def reset(self) -> None:
        self._samples.clear()
        self._started_at = None
        self._finished = False
        self._result = None

    def start(self) -> None:
        self.reset()
        self._started_at = time.perf_counter()

    def add_sample(self, ear: float) -> CalibrationResult | None:
        if self._finished or self._started_at is None:
            return self._result

        elapsed = time.perf_counter() - self._started_at
        if elapsed >= self.duration_seconds:
            return self._finalize()

        if len(self._samples) < 5:
            self._samples.append(ear)
            return None

        running_mean = float(np.mean(self._samples))
        if ear >= running_mean * self.open_eye_ratio:
            self._samples.append(ear)

        return None

    def _finalize(self) -> CalibrationResult:
        if self._result is not None:
            return self._result

        if not self._samples:
            self._result = CalibrationResult(
                ear_threshold=0.24,
                baseline_ear_mean=0.32,
                sample_count=0,
            )
        else:
            sorted_samples = sorted(self._samples)
            trim = max(1, int(len(sorted_samples) * self.trim_percent))
            trimmed = sorted_samples[trim:-trim] if len(sorted_samples) > trim * 2 else sorted_samples
            baseline = float(np.mean(trimmed))
            self._result = CalibrationResult(
                ear_threshold=baseline * self.threshold_multiplier,
                baseline_ear_mean=baseline,
                sample_count=len(trimmed),
            )

        self._finished = True
        return self._result

    def force_complete(self) -> CalibrationResult:
        return self._finalize()
