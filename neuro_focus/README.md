# Neuro-Focus

A desktop **behavioral analytics platform** for students — a personal study operating system that uses real-time computer vision biomarkers (blink rate, blink duration) to support focus sessions, journaling, and weekly insights.

Built with **PyQt6**, **OpenCV**, **MediaPipe**, and **NumPy**.

---

## Product positioning

Not a webcam demo. Neuro-Focus is a productivity platform (Notion / Forest / Opal inspired) where CV is one layer in a larger study system:

- **Home** — today's progress, streak, insights, start focus
- **Sessions** — structured session history
- **Analytics** — weekly trends and subject comparisons
- **Journal** — reflections and distraction logs
- **Settings** — personalization

Live camera tracking only appears inside an active **Focus Session** (after category selection + calibration).

---

## Setup

```bash
source ../neuro_env/bin/activate
pip install -r requirements.txt

curl -L -o face_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"

python main.py
```

Run from repo root: `python neuro_focus/main.py`

---

## Architecture

```
neuro_focus/
├── main.py
├── ui/
│   ├── main_window.py       # Shell + bottom nav
│   ├── home_view.py         # Home dashboard
│   ├── focus_session.py     # Calibration + live tracking
│   ├── sessions_view.py
│   ├── analytics_view.py
│   ├── journal_view.py
│   ├── settings_view.py
│   └── widgets/             # Camera, stat cards, nav
├── engine/
│   ├── tracker.py
│   ├── calibration.py
│   └── metrics.py
├── session/
│   ├── session_manager.py
│   └── analytics.py
└── data/
```

---

## Metrics (defensible MVP)

**Focus score** — starts at 100, penalized by:
- fatigue events (blinks ≥ 0.4s)
- BPM variability
- blink-rate spikes

**Fatigue score** — long-blink events per hour

These are behavioral signals, not clinical neuroscience claims.

---

## Future features

- Posture / neck angle tracking (shoulder landmarks + calibration)
- macOS `.app` packaging
- Session charts in Analytics

---

## Branch

`feature/neuro-focus-desktop-app`
