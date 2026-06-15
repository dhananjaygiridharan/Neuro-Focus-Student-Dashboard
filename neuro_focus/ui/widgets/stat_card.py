from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StatCard(QFrame):
    def __init__(self, label: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(4)
        self.value_label = QLabel("—")
        self.value_label.setObjectName("statValue")
        self.title_label = QLabel(label.upper())
        self.title_label.setObjectName("statLabel")
        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)

    def set_value(self, text: str) -> None:
        self.value_label.setText(text)
