"""System configuration and academic constants for EduTrack.

Defines University academic parameters such as attendance thresholds,
grading scale, assessment weightage, and default storage file paths.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

STORAGE_FILE = DATA_DIR / "edutrack_data.json"

# Academic Regulations (VIT Standard)
MIN_ATTENDANCE_PERCENTAGE = 75.0  # Threshold for exam eligibility
ATTENDANCE_WARNING_PERCENTAGE = 80.0

# 10-Point Relative / Absolute Grade Scale
GRADE_SCALE = [
    ("S", 90.0, 10),
    ("A", 80.0, 9),
    ("B", 70.0, 8),
    ("C", 60.0, 7),
    ("D", 50.0, 6),
    ("E", 40.0, 5),
    ("F", 0.0, 0),
]

# Assessment Maximum Marks
ASSESSMENT_MAX_MARKS = {
    "quiz": 10.0,
    "assignment": 20.0,
    "midterm": 30.0,
    "final": 40.0,
}

TOTAL_MARKS = 100.0
