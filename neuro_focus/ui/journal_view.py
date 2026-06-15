"""Study journal — reflections and distractions."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from neuro_focus.session.session_manager import SessionManager


class JournalView(QWidget):
    def __init__(self, session_manager: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self.session_manager = session_manager
        self._selected_id: str | None = None
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

        title = QLabel("Journal")
        title.setObjectName("sectionTitle")
        left_layout.addWidget(title)
        subtitle = QLabel("Session reflections and distraction logs")
        subtitle.setObjectName("muted")
        left_layout.addWidget(subtitle)

        self.entry_list = QListWidget()
        self.entry_list.currentItemChanged.connect(self._on_selected)
        left_layout.addWidget(self.entry_list)
        root.addWidget(left, stretch=1)

        right = QFrame()
        right.setObjectName("panel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 20, 20, 20)

        self.entry_title = QLabel("Select an entry")
        self.entry_title.setObjectName("sectionTitle")
        right_layout.addWidget(self.entry_title)

        for label_text, attr in [
            ("What you studied", "what_edit"),
            ("How focused you felt", "rating_edit"),
            ("Distractions", "distraction_edit"),
            ("Reflection", "reflection_edit"),
        ]:
            lbl = QLabel(label_text)
            lbl.setObjectName("statLabel")
            edit = QTextEdit()
            edit.setMaximumHeight(90 if attr != "reflection_edit" else 120)
            setattr(self, attr, edit)
            right_layout.addWidget(lbl)
            right_layout.addWidget(edit)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_btn = QPushButton("Update Reflection")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save)
        save_row.addWidget(self.save_btn)
        right_layout.addLayout(save_row)
        root.addWidget(right, stretch=2)

    def refresh(self) -> None:
        sessions = {s["session_id"]: s for s in SessionManager.load_all_sessions()}
        entries = SessionManager.load_all_journal_entries()
        self.entry_list.clear()

        if not entries and not sessions:
            item = QListWidgetItem("Complete a session to start your journal")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.entry_list.addItem(item)
            return

        seen = set()
        for entry in entries:
            sid = entry.get("session_id", "")
            seen.add(sid)
            session = sessions.get(sid, {})
            label = f"{session.get('category', 'Session')} · {entry.get('updated_at', '')[:10]}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, sid)
            self.entry_list.addItem(item)

        for sid, session in sessions.items():
            if sid in seen:
                continue
            item = QListWidgetItem(f"{session.get('category', 'Session')} · (no journal yet)")
            item.setData(Qt.ItemDataRole.UserRole, sid)
            self.entry_list.addItem(item)

        if self.entry_list.count():
            self.entry_list.setCurrentRow(0)

    def _on_selected(self, current: QListWidgetItem | None, _previous=None) -> None:
        if current is None:
            return
        session_id = current.data(Qt.ItemDataRole.UserRole)
        if not session_id:
            return

        self._selected_id = session_id
        entry = SessionManager.load_journal_entry(session_id)
        sessions = {s["session_id"]: s for s in SessionManager.load_all_sessions()}
        session = sessions.get(session_id, {})

        self.entry_title.setText(session.get("task_description") or session.get("category", "Entry"))
        self.what_edit.setPlainText(entry.get("what_studied", session.get("category", "")))
        self.rating_edit.setPlainText(entry.get("focus_rating", ""))
        self.distraction_edit.setPlainText(entry.get("distractions", ""))
        self.reflection_edit.setPlainText(entry.get("reflection", session.get("notes", "")))
        self.save_btn.setEnabled(True)

    def _save(self) -> None:
        if not self._selected_id:
            return
        SessionManager.save_journal_entry(
            self._selected_id,
            {
                "what_studied": self.what_edit.toPlainText().strip(),
                "focus_rating": self.rating_edit.toPlainText().strip(),
                "distractions": self.distraction_edit.toPlainText().strip(),
                "reflection": self.reflection_edit.toPlainText().strip(),
            },
        )
        self.refresh()
