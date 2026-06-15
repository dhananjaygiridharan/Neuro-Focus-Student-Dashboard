"""Pure metrics calculations — no CV or UI dependencies."""

from __future__ import annotations

import statistics
from collections import deque

LONG_BLINK_THRESHOLD_SEC = 0.4
BASELINE_BPM = 15.0


def compute_bpm(blink_times: deque[float], window_seconds: float = 60.0) -> float:
    """Rolling blinks-per-minute from recent blink timestamps."""
    if not blink_times:
        return 0.0
    now = blink_times[-1]
    recent = [t for t in blink_times if now - t <= window_seconds]
    if not recent:
        return 0.0
    span = min(window_seconds, now - recent[0]) if len(recent) > 1 else window_seconds
    if span <= 0:
        return 0.0
    return (len(recent) / span) * 60.0


def average_blink_duration(blink_durations: deque[float]) -> float:
    if not blink_durations:
        return 0.0
    return sum(blink_durations) / len(blink_durations)


def is_fatigue_event(blink_duration: float, threshold: float = LONG_BLINK_THRESHOLD_SEC) -> bool:
    """A long blink counts as one fatigue event."""
    return blink_duration >= threshold


def fatigue_score_from_events(fatigue_events: int, session_hours: float) -> float:
    """
    Fatigue score based on long-blink events per hour.
    Higher = more fatigue signal. Capped at 100.
    """
    if session_hours <= 0 or fatigue_events <= 0:
        return 0.0
    events_per_hour = fatigue_events / session_hours
    return min(100.0, events_per_hour * 12.0)


def focus_score(
    bpm_samples: list[float],
    fatigue_events: int,
    *,
    baseline_bpm: float = BASELINE_BPM,
    spike_threshold: float = 1.35,
) -> float:
    """
    Session focus score starting at 100, with interpretable penalties:
    - fatigue events
    - excessive blink-rate spikes
    - BPM variability (instability)
    """
    score = 100.0
    score -= min(45.0, fatigue_events * 4.0)

    if len(bpm_samples) >= 3:
        variability = statistics.stdev(bpm_samples)
        score -= min(25.0, variability * 1.8)

    if bpm_samples:
        peak_bpm = max(bpm_samples)
        if peak_bpm > baseline_bpm * spike_threshold:
            overshoot = (peak_bpm / baseline_bpm) - spike_threshold
            score -= min(20.0, overshoot * 40.0)

    return max(0.0, min(100.0, score))


def live_focus_estimate(
    bpm: float,
    fatigue_events: int,
    elapsed_minutes: float,
    bpm_samples: list[float],
) -> float:
    """Lightweight in-session focus estimate for the live UI."""
    projected_events = fatigue_events
    if elapsed_minutes > 0:
        rate = fatigue_events / max(elapsed_minutes / 60.0, 0.05)
        projected_events = int(rate * max(elapsed_minutes / 60.0, 0.05))
    return focus_score(bpm_samples or [bpm], projected_events)


def attention_state(
    bpm: float,
    baseline_bpm: float,
    avg_blink_duration: float,
    total_blinks: int,
    fatigue_events: int,
    *,
    is_calibrated: bool = True,
    bpm_drop_threshold: float = 0.85,
    duration_threshold: float = LONG_BLINK_THRESHOLD_SEC,
) -> str:
    if not is_calibrated:
        return "Calibrating Baseline..."

    if total_blinks == 0 and bpm == 0:
        return "Neutral State"

    cond_focus = bpm < (baseline_bpm * bpm_drop_threshold)
    cond_fatigue = avg_blink_duration >= duration_threshold or fatigue_events > 0

    if cond_focus and cond_fatigue:
        return "Focused with Fatigue Signals"
    if cond_focus:
        return "Stable Focus"
    if cond_fatigue:
        return "Fatigue Detected"
    return "Neutral State"
