"""Session lifecycle, metadata, and periodic CSV logging."""

from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
NOTES_DIR = os.path.join(DATA_DIR, "notes")
JOURNAL_DIR = os.path.join(DATA_DIR, "journal")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
SESSIONS_CSV = os.path.join(DATA_DIR, "sessions.csv")
SESSION_FIELDS = [
    "session_id",
    "category",
    "urgency",
    "task_description",
    "start_time",
    "end_time",
    "duration_seconds",
    "total_blinks",
    "avg_bpm",
    "avg_ear",
    "avg_blink_duration",
    "focus_score",
    "fatigue_events",
    "notes",
    "raw_file",
]


@dataclass
class SessionMetadata:
    session_id: str
    category: str
    urgency: str
    task_description: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0
    total_blinks: int = 0
    avg_bpm: float = 0.0
    avg_ear: float = 0.0
    avg_blink_duration: float = 0.0
    focus_score: float = 0.0
    fatigue_events: int = 0
    notes: str = ""
    raw_file: str = ""
    _log_samples: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def to_row(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in SESSION_FIELDS}


class SessionManager:
    def __init__(self, log_interval_seconds: float = 3.0) -> None:
        self.log_interval_seconds = log_interval_seconds
        self.active: SessionMetadata | None = None
        self._last_log_time = 0.0
        self._raw_writer: csv.writer | None = None
        self._raw_file_handle = None
        self._ensure_directories()

    @staticmethod
    def _ensure_directories() -> None:
        os.makedirs(RAW_DIR, exist_ok=True)
        os.makedirs(NOTES_DIR, exist_ok=True)
        os.makedirs(JOURNAL_DIR, exist_ok=True)
        if not os.path.isfile(SESSIONS_CSV):
            with open(SESSIONS_CSV, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=SESSION_FIELDS).writeheader()

    @staticmethod
    def _slug(text: str) -> str:
        return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")[:32]

    def start_session(
        self,
        category: str,
        urgency: str,
        task_description: str = "",
        pre_session_notes: str = "",
    ) -> SessionMetadata:
        if self.active is not None:
            self.end_session()

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{stamp}_{self._slug(category)}"
        raw_filename = f"{session_id}.csv"
        raw_path = os.path.join(RAW_DIR, raw_filename)

        self.active = SessionMetadata(
            session_id=session_id,
            category=category,
            urgency=urgency,
            task_description=task_description,
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            notes=pre_session_notes,
            raw_file=raw_filename,
        )

        self._raw_file_handle = open(raw_path, "w", newline="", encoding="utf-8")
        self._raw_writer = csv.writer(self._raw_file_handle)
        self._raw_writer.writerow(
            [
                "timestamp",
                "ear",
                "bpm",
                "blink_count",
                "avg_blink_duration",
                "cognitive_state",
                "fatigue",
                "focus",
                "fatigue_events",
            ]
        )
        self._last_log_time = time.perf_counter()
        return self.active

    def log_frame_state(self, state: dict[str, Any]) -> None:
        if self.active is None or self._raw_writer is None:
            return

        now = time.perf_counter()
        if now - self._last_log_time < self.log_interval_seconds:
            return

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"{state.get('ear', 0):.4f}",
            f"{state.get('bpm', 0):.2f}",
            state.get("blink_count", 0),
            f"{state.get('avg_blink_duration', 0):.4f}",
            state.get("cognitive_state", ""),
            f"{state.get('fatigue', 0):.1f}",
            f"{state.get('focus', 0):.1f}",
            state.get("fatigue_events", 0),
        ]
        self._raw_writer.writerow(row)
        self._raw_file_handle.flush()
        self._last_log_time = now

        self.active._log_samples.append(
            {
                "bpm": float(state.get("bpm", 0)),
                "ear": float(state.get("ear", 0)),
                "blink_count": int(state.get("blink_count", 0)),
                "avg_blink_duration": float(state.get("avg_blink_duration", 0)),
                "focus": float(state.get("focus", 0)),
            }
        )

    @staticmethod
    def save_notes_for_session(session_id: str, notes: str) -> None:
        os.makedirs(NOTES_DIR, exist_ok=True)
        note_path = os.path.join(NOTES_DIR, f"{session_id}.json")
        with open(note_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "session_id": session_id,
                    "notes": notes,
                    "updated_at": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    @staticmethod
    def save_journal_entry(session_id: str, entry: dict[str, Any]) -> None:
        os.makedirs(JOURNAL_DIR, exist_ok=True)
        path = os.path.join(JOURNAL_DIR, f"{session_id}.json")
        payload = {"session_id": session_id, **entry, "updated_at": datetime.now().isoformat()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def load_journal_entry(session_id: str) -> dict[str, Any]:
        path = os.path.join(JOURNAL_DIR, f"{session_id}.json")
        if not os.path.isfile(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_all_journal_entries() -> list[dict[str, Any]]:
        if not os.path.isdir(JOURNAL_DIR):
            return []
        entries = []
        for name in os.listdir(JOURNAL_DIR):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(JOURNAL_DIR, name), encoding="utf-8") as f:
                entries.append(json.load(f))
        entries.sort(key=lambda e: e.get("updated_at", ""), reverse=True)
        return entries

    @staticmethod
    def load_settings() -> dict[str, Any]:
        if not os.path.isfile(SETTINGS_PATH):
            return {"display_name": "", "fatigue_nudges": True}
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_settings(settings: dict[str, Any]) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def update_notes(self, notes: str) -> None:
        if self.active is None:
            return
        self.active.notes = notes
        self.save_notes_for_session(self.active.session_id, notes)

    def end_session(self, final_state: dict[str, Any] | None = None) -> SessionMetadata | None:
        if self.active is None:
            return None

        if final_state:
            self.log_frame_state(final_state)

        self.active.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_dt = datetime.strptime(self.active.start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(self.active.end_time, "%Y-%m-%d %H:%M:%S")
        self.active.duration_seconds = (end_dt - start_dt).total_seconds()

        if final_state:
            self.active.total_blinks = int(final_state.get("blink_count", 0))
            self.active.fatigue_events = int(final_state.get("fatigue_events", 0))
            self.active.focus_score = float(final_state.get("focus_score", final_state.get("focus", 0)))
            self.active.avg_blink_duration = float(final_state.get("avg_blink_duration", 0))

        samples = self.active._log_samples
        if samples:
            self.active.avg_bpm = sum(s["bpm"] for s in samples) / len(samples)
            self.active.avg_ear = sum(s["ear"] for s in samples) / len(samples)
            if not final_state or not self.active.avg_blink_duration:
                self.active.avg_blink_duration = sum(
                    s.get("avg_blink_duration", 0) for s in samples
                ) / len(samples)
            if not final_state:
                self.active.total_blinks = max(s["blink_count"] for s in samples)

        if self._raw_file_handle:
            self._raw_file_handle.close()
            self._raw_file_handle = None
            self._raw_writer = None

        self._append_session_row(self.active)
        finished = self.active
        self.active = None
        return finished

    def _append_session_row(self, session: SessionMetadata) -> None:
        with open(SESSIONS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=SESSION_FIELDS)
            writer.writerow(session.to_row())

    @staticmethod
    def load_all_sessions() -> list[dict[str, Any]]:
        if not os.path.isfile(SESSIONS_CSV):
            return []
        with open(SESSIONS_CSV, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def load_raw_session(filename: str) -> list[dict[str, str]]:
        path = os.path.join(RAW_DIR, filename)
        if not os.path.isfile(path):
            return []
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def load_session_notes(session_id: str) -> str:
        path = os.path.join(NOTES_DIR, f"{session_id}.json")
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("notes", "")

    @property
    def is_active(self) -> bool:
        return self.active is not None
