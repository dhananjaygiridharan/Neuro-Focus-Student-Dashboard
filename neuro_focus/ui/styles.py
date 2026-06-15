"""Deep matte dark theme — Notion / Linear / Opal inspired."""

APP_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #080808;
    color: #f0f0f0;
}

QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    color: #f0f0f0;
}

QFrame#bottomNav {
    background-color: #0c0c0c;
    border-top: 1px solid #1c1c1c;
}

QFrame#panel {
    background-color: #101010;
    border: 1px solid #1c1c1c;
    border-radius: 14px;
}

QFrame#heroCard {
    background-color: #101010;
    border: 1px solid #1c1c1c;
    border-radius: 16px;
}

QFrame#statCard {
    background-color: #121212;
    border: 1px solid #222222;
    border-radius: 12px;
}

QFrame#cameraFrame {
    background-color: #000000;
    border: 1px solid #1c1c1c;
    border-radius: 16px;
}

QFrame#insightCard {
    background-color: #0e0e0e;
    border: 1px solid #242424;
    border-radius: 12px;
}

QLabel#appTitle {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.2px;
}

QLabel#muted {
    color: #6b6b6b;
}

QLabel#statValue {
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}

QLabel#statLabel {
    font-size: 10px;
    font-weight: 600;
    color: #5a5a5a;
    letter-spacing: 0.8px;
}

QPushButton#bottomNavButton {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    color: #5a5a5a;
    font-weight: 500;
}

QPushButton#bottomNavButton:hover {
    background-color: #141414;
    color: #d0d0d0;
}

QPushButton#bottomNavButton[active="true"] {
    background-color: #181818;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryButton {
    background-color: #f0f0f0;
    color: #080808;
    border: none;
    border-radius: 10px;
    padding: 12px 22px;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #ffffff;
}

QPushButton#primaryButton:disabled {
    background-color: #1a1a1a;
    color: #444444;
}

QPushButton#heroButton {
    background-color: #ffffff;
    color: #080808;
    border: none;
    border-radius: 12px;
    padding: 16px 28px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton#heroButton:hover {
    background-color: #e8e8e8;
}

QPushButton#dangerButton {
    background-color: #1a1a1a;
    color: #ff6b6b;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton#dangerButton:hover {
    background-color: #222222;
    border-color: #ff6b6b;
}

QPushButton#dangerButton:disabled {
    color: #444444;
    border-color: #1a1a1a;
}

QPushButton#ghostButton {
    background-color: #121212;
    color: #d0d0d0;
    border: 1px solid #222222;
    border-radius: 10px;
    padding: 8px 14px;
}

QPushButton#ghostButton:hover {
    background-color: #181818;
}

QComboBox, QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox {
    background-color: #101010;
    border: 1px solid #222222;
    border-radius: 10px;
    padding: 10px 12px;
    color: #f0f0f0;
    selection-background-color: #333333;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #101010;
    border: 1px solid #222222;
    selection-background-color: #222222;
}

QListWidget {
    background-color: #0c0c0c;
    border: 1px solid #1c1c1c;
    border-radius: 12px;
    outline: none;
}

QListWidget::item {
    padding: 14px;
    border-bottom: 1px solid #141414;
}

QListWidget::item:selected {
    background-color: #161616;
    color: #ffffff;
}

QScrollBar:vertical {
    background: #0a0a0a;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #2a2a2a;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QProgressBar {
    background-color: #141414;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #d0d0d0;
    border-radius: 4px;
}

QFrame#nudgeBanner {
    background-color: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
}
"""

STATUS_COLORS = {
    "idle": "#5a5a5a",
    "calibrating": "#c9a227",
    "tracking": "#4ade80",
    "no_face": "#ff6b6b",
}

CATEGORY_OPTIONS = [
    "Biology",
    "Chemistry",
    "Math",
    "English",
    "Coding",
    "Reading",
    "Other",
]

URGENCY_OPTIONS = ["Low", "Medium", "High", "Critical"]

FOCUS_RATING_OPTIONS = ["1 — Very distracted", "2", "3 — Neutral", "4", "5 — Deeply focused"]
