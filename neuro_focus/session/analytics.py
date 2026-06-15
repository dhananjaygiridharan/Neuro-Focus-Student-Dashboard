"""Aggregated study analytics — streaks, insights, weekly trends."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


def _parse_dt(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _session_date(session: dict[str, Any]) -> datetime | None:
    return _parse_dt(session.get("start_time", ""))


def today_study_seconds(sessions: list[dict[str, Any]]) -> float:
    today = datetime.now().date()
    total = 0.0
    for session in sessions:
        start = _session_date(session)
        if start and start.date() == today:
            total += float(session.get("duration_seconds") or 0)
    return total


def format_duration(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def study_streak_days(sessions: list[dict[str, Any]]) -> int:
    dates = sorted(
        {d.date() for s in sessions if (d := _session_date(s)) is not None},
        reverse=True,
    )
    if not dates:
        return 0

    streak = 0
    expected = datetime.now().date()
    if dates[0] != expected and dates[0] != expected - timedelta(days=1):
        return 0

    for day in dates:
        if day == expected or day == expected - timedelta(days=1):
            streak += 1
            expected = day - timedelta(days=1)
        else:
            break
    return streak


def last_session(sessions: list[dict[str, Any]]) -> dict[str, Any] | None:
    dated = [(s, _session_date(s)) for s in sessions]
    dated = [(s, d) for s, d in dated if d is not None]
    if not dated:
        return None
    return max(dated, key=lambda item: item[1])[0]


def recommended_block_minutes(sessions: list[dict[str, Any]]) -> int:
    """Suggest a study block based on recent successful session lengths."""
    durations = [
        float(s.get("duration_seconds") or 0) / 60.0
        for s in sessions[-8:]
        if float(s.get("focus_score") or 0) >= 70
    ]
    if not durations:
        return 45
    avg = sum(durations) / len(durations)
    return max(25, min(60, int(round(avg / 5) * 5)))


def focus_insight(sessions: list[dict[str, Any]]) -> str:
    """Generate a simple, defensible insight from session history."""
    if len(sessions) < 2:
        return "Complete a few sessions to unlock personalized focus insights."

    drop_minutes: list[float] = []
    for session in sessions[-12:]:
        raw_file = session.get("raw_file", "")
        if not raw_file:
            continue
        from neuro_focus.session.session_manager import SessionManager

        rows = SessionManager.load_raw_session(raw_file)
        if len(rows) < 4:
            continue
        focus_vals = []
        for row in rows:
            try:
                focus_vals.append(float(row.get("focus", 0)))
            except (TypeError, ValueError):
                continue
        if len(focus_vals) < 4:
            continue
        peak = max(focus_vals[: max(1, len(focus_vals) // 3)])
        for i, val in enumerate(focus_vals):
            if val < peak * 0.75:
                drop_minutes.append(i * 3 / 60.0)
                break

    if drop_minutes:
        avg_drop = sum(drop_minutes) / len(drop_minutes)
        rounded = max(20, min(55, int(round(avg_drop / 5) * 5)))
        return (
            f"Your focus tends to drop after about {rounded} minutes. "
            f"Consider a short break around {max(15, rounded - 5)} minutes."
        )

    best = max(sessions, key=lambda s: float(s.get("focus_score") or 0), default=None)
    if best:
        cat = best.get("category", "study")
        return f"Your strongest sessions are in {cat}. Schedule deep work there when possible."

    return "Keep logging sessions — patterns will emerge as your data grows."


def weekly_summary(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    cutoff = datetime.now() - timedelta(days=7)
    week = [s for s in sessions if (d := _session_date(s)) and d >= cutoff]

    total_seconds = sum(float(s.get("duration_seconds") or 0) for s in week)
    focus_scores = [float(s.get("focus_score") or 0) for s in week if s.get("focus_score")]
    fatigue_events = sum(int(s.get("fatigue_events") or 0) for s in week)

    by_category: dict[str, list[float]] = defaultdict(list)
    for s in week:
        by_category[s.get("category", "Other")].append(float(s.get("focus_score") or 0))

    best_subject = "—"
    worst_subject = "—"
    if by_category:
        avgs = {k: sum(v) / len(v) for k, v in by_category.items() if v}
        if avgs:
            best_subject = max(avgs, key=avgs.get)
            worst_subject = min(avgs, key=avgs.get)

    return {
        "session_count": len(week),
        "total_hours": total_seconds / 3600.0,
        "avg_focus": sum(focus_scores) / len(focus_scores) if focus_scores else 0.0,
        "total_fatigue_events": fatigue_events,
        "best_subject": best_subject,
        "worst_subject": worst_subject,
        "avg_bpm": _avg_field(week, "avg_bpm"),
        "avg_blink_duration": _avg_field(week, "avg_blink_duration"),
    }


def _avg_field(sessions: list[dict[str, Any]], field: str) -> float:
    vals = []
    for s in sessions:
        try:
            vals.append(float(s.get(field) or 0))
        except (TypeError, ValueError):
            continue
    return sum(vals) / len(vals) if vals else 0.0


def greeting_name(default: str = "there") -> str:
    from neuro_focus.session.session_manager import SessionManager

    settings = SessionManager.load_settings()
    return settings.get("display_name") or default


def time_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"
