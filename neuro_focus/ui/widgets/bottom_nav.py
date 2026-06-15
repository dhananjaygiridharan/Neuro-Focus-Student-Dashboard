from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton


class BottomNavBar(QFrame):
    page_selected = pyqtSignal(int)

    NAV_ITEMS = [
        ("Home", 0),
        ("Sessions", 1),
        ("Analytics", 2),
        ("Journal", 3),
        ("Settings", 4),
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("bottomNav")
        self._buttons: list[QPushButton] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(8)

        for label, index in self.NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("bottomNavButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("active", index == 0)
            btn.clicked.connect(lambda checked=False, i=index, b=btn: self._select(i, b))
            layout.addWidget(btn)
            self._buttons.append(btn)

        self._polish_all()

    def set_active(self, index: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.setProperty("active", i == index)
        self._polish_all()

    def _select(self, index: int, active_btn: QPushButton) -> None:
        for btn in self._buttons:
            btn.setProperty("active", btn is active_btn)
        self._polish_all()
        self.page_selected.emit(index)

    def _polish_all(self) -> None:
        for btn in self._buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
