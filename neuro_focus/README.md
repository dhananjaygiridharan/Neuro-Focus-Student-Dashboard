# Neuro-Focus: Real-Time Study Fatigue & Attention Tracking

## Overview

Neuro-Focus is a desktop application that uses computer vision to monitor spontaneous eye blink behavior during study sessions. Using a webcam and facial landmark detection, the system tracks Eye Aspect Ratio (EAR), blink frequency, blink duration, and other behavioral metrics to estimate focus and fatigue in real time.

The project combines computer vision, signal processing, data logging, and desktop application development into a single productivity-focused tool.

---

## Features

* Real-time webcam-based eye tracking
* MediaPipe facial landmark detection
* Eye Aspect Ratio (EAR) calculation
* Adaptive user calibration
* Blink detection using temporal state-machine logic
* Real-time blinks-per-minute (BPM) tracking
* Average blink duration tracking
* Fatigue state classification
* Study session management
* Session data logging and storage
* Desktop application built with PyQt6

---

## How It Works

1. MediaPipe Face Landmarker detects facial landmarks from a webcam feed.
2. Eye landmarks are used to calculate Eye Aspect Ratio (EAR).
3. A blink detection state machine identifies valid blinks while filtering noise.
4. Blink frequency and duration metrics are tracked throughout a study session.
5. Behavioral metrics are analyzed to estimate attention and fatigue states.
6. Session data is saved for later review and analysis.

---

## Technologies Used

* Python
* OpenCV
* MediaPipe
* NumPy
* Pandas
* PyQt6

---

## Project Structure

```text
neuro_focus/
│
├── main.py
│
├── ui/
│   ├── main_window.py
│   ├── dashboard.py
│   └── session_view.py
│
├── engine/
│   ├── tracker.py
│   ├── calibration.py
│   └── metrics.py
│
├── session/
│   └── session_manager.py
│
├── data/
│   ├── raw/
│   └── sessions.csv
│
├── assets/
│
├── face_landmarker.task
├── requirements.txt
└── README.md
```

---

## Installation

Create and activate a virtual environment:

```bash
python -m venv neuro_env
source neuro_env/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## What I Learned

Through this project I gained experience with:

* Real-time computer vision pipelines
* Facial landmark detection
* Signal processing and behavioral metrics
* State machine design
* Data logging and session management
* PyQt6 desktop application development
* Git and GitHub workflows
* Software architecture and project organization

---

## Disclaimer

Neuro-Focus is an educational and experimental project. It is not intended to diagnose medical conditions or provide clinical assessments of attention, fatigue, or cognitive performance.
