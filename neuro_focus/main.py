"""Neuro-Focus desktop application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

# Support running as `python main.py` from neuro_focus/ or `python -m neuro_focus.main`
_pkg_root = Path(__file__).resolve().parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from PyQt6.QtWidgets import QApplication, QMessageBox

from neuro_focus.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Neuro-Focus")
    app.setOrganizationName("Neuro-Focus")

    try:
        window = MainWindow()
    except FileNotFoundError as exc:
        QMessageBox.critical(
            None,
            "Missing Model File",
            str(exc)
            + "\n\nDownload from:\n"
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
            "face_landmarker/float16/latest/face_landmarker.task",
        )
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
