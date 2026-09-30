# EduTrack

**Academic Performance & Attendance Monitoring System**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-2.6.0-informational.svg)](edutrack/__init__.py)
[![Tests](https://img.shields.io/badge/tests-16%20passed-success.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

EduTrack is a lightweight, modular Python application designed for university academic workflows. It simplifies student course registration, automates attendance tracking according to the mandatory **75% minimum attendance policy**, computes credit-weighted Semester Grade Point Averages (SGPA), and generates exportable institutional audit reports.

Built with Python's standard library — zero external dependencies required.

---

## Table of Contents

- [Why EduTrack?](#why-edutrack)
- [Key Features](#key-features)
- [Grading System](#grading-system)
- [Quick Start](#quick-start)
- [Project Architecture](#project-architecture)
- [Running Unit Tests](#running-unit-tests)
- [Sample Usage](#sample-usage)
- [Contributing](#contributing)
- [License](#license)

---

## Why EduTrack?

In collegiate systems with continuous assessment, students frequently struggle with:
1. **Attendance Debarment**: Falling below 75% attendance without early warning, leading to exam debarment.
2. **Margin Calculation**: Inability to easily determine how many upcoming lectures must be attended to recover or how many can be safely missed.
3. **Complex GPA Calculations**: Manually computing weighted SGPA across theory and lab courses with different credit allocations (1 to 5 credits) and multi-part marking schemes (Quizzes, Assignments, Midterms, Final Exam).

EduTrack addresses these issues through automated margin prediction, instant debarment alerts, and accurate GPA computation.

---

## Key Features

- **Attendance Monitoring & 75% Rule Compliance**:
  - Live calculation of attendance percentage per enrolled course.
  - **Predictive Margin Advice**:
    - If `< 75%`: Calculates the exact number of consecutive classes required to regain eligibility.
    - If `≥ 75%`: Calculates the safe attendance buffer (classes that can be missed without dropping below threshold).
  - One-click listing of all debarred students across sections.

- **Credit-Weighted SGPA & Marks Evaluation**:
  - Supports 4-component continuous assessments: Quiz (10), Assignment (20), Midterm (30), and Final Examination (40).
  - Converts aggregate scores (out of 100) to standard letter grades (`S`, `A`, `B`, `C`, `D`, `E`, `F`).
  - Automatic GPA weighting based on individual course credit values.

- **Student & Course Administration**:
  - Full CRUD operations for student profiles with format validation (Reg No: e.g., `26BCE1001`).
  - Course offering catalog with seat capacity enforcement and drop workflows.

- **Institutional Analytics & CSV Exports**:
  - Course-level metrics: class average, pass rate, highest/lowest marks.
  - **Dean's Honor Roll**: Live leaderboard ranking top academic performers.
  - Atomic export to CSV spreadsheets (`students_report.csv` and `attendance_summary.csv`).

- **Zero Third-Party Dependencies**:
  - Pure Python standard library implementation (`re`, `json`, `csv`, `unittest`).

---

## Grading System

EduTrack implements the university 10-point relative/absolute grading scale:

| Mark Range (out of 100) | Letter Grade | Grade Point | Status |
|:---|:---:|:---:|:---|
| 90 – 100 | **S** | 10 | PASS |
| 80 – 89 | **A** | 9 | PASS |
| 70 – 79 | **B** | 8 | PASS |
| 60 – 69 | **C** | 7 | PASS |
| 50 – 59 | **D** | 6 | PASS |
| 40 – 49 | **E** | 5 | PASS |
| < 40 | **F** | 0 | FAIL |
| Debarred (< 75% attendance) | **F (Debarred)** | 0 | DEBARRED |

*Note: Any student with attendance below 75% is automatically assigned an `F (Debarred)` grade with 0 grade points, irrespective of their assessment marks.*

---

## Quick Start

### Prerequisites
- Python 3.8 or higher.

### 1. Clone the Repository
```bash
git clone https://github.com/karnavkhare1-tech/Vityarthi-project.git
cd Vityarthi-project
```

### 2. Run the Interactive Application
```bash
python main.py
```

### 3. Run the Automated Demo
To run the full end-to-end demonstration (seeds initial data, enrolls students, logs attendance, calculates GPA, and writes CSV reports):
```bash
python demo.py
```

---

## Project Architecture

The system follows a clean, modular layered architecture:

```text
Vityarthi-project/
├── edutrack/
│   ├── cli/
│   │   └── menu.py               # Formatted terminal UI and controllers
│   ├── models/
│   │   ├── person.py             # Base Person and Faculty models
│   │   ├── student.py            # Student and CourseRecord models
│   │   └── course.py             # Academic Course model
│   ├── services/
│   │   ├── student_service.py    # Student CRUD and search logic
│   │   ├── course_service.py     # Catalog and seat enrollment logic
│   │   ├── attendance_service.py # Attendance tracking and 75% rule audit
│   │   └── analytics_service.py  # Marks recording, SGPA, and leaderboard
│   ├── storage/
│   │   └── file_storage.py       # Atomic JSON storage & CSV export engine
│   ├── utils/
│   │   ├── exceptions.py         # Custom domain exceptions
│   │   └── validators.py         # RegEx-based sanitizers and format checks
│   ├── config.py                 # Academic constants and file paths
│   └── data_seed.py              # Sample dataset generation
├── tests/
│   ├── test_models.py            # Model behavior and GPA calculation tests
│   ├── test_services.py          # Business workflows and CRUD tests
│   └── test_validators.py        # Input boundary and regex tests
├── data/
│   └── edutrack_data.json        # Persistent JSON state file
├── reports/
│   ├── students_report.csv       # Exported student SGPA summary
│   └── attendance_summary.csv    # Exported attendance audit report
├── main.py                       # CLI application entry point
├── demo.py                       # Automated end-to-end verification script
├── generate_report_doc.py        # HTML documentation generator
├── PROJECT_REPORT.md             # Comprehensive technical report
└── README.md                     # Project documentation
```

---

## Running Unit Tests

The test suite covers model logic, attendance boundaries, duplicate detection, score validations, and credit-weighted SGPA formulas.

Run all tests using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests
```

Expected output:
```text
................
----------------------------------------------------------------------
Ran 16 tests in 0.002s

OK
```

---

## Sample Usage

### 1. Academic Transcript & Weighted GPA
```text
==========================================================================================
ACADEMIC TRANSCRIPT: Aarav Sharma (26BCE1001)
Branch: BCE | Semester: 1 | Total Credits: 11
==========================================================================================
Course     | Title                     | Cr  | Quiz  | Asgn  | Mid   | Fin   | Tot   | Att%   | Grd  | Status
------------------------------------------------------------------------------------------
CSE1001    | Problem Solving and Progr | 4   | 9.5   | 19.0  | 28.0  | 38.0  | 94.5  | 93.3   | S    | PASS
MAT1001    | Calculus and Linear Algeb | 4   | 8.5   | 18.0  | 26.0  | 35.0  | 87.5  | 90.0   | A    | PASS
PHY1001    | Engineering Physics       | 3   | 9.0   | 17.5  | 27.0  | 36.0  | 89.5  | 91.7   | A    | PASS
==========================================================================================
SEMESTER GRADE POINT AVERAGE (SGPA): 9.36 / 10.00
==========================================================================================
```

### 2. Predictive Attendance Recovery Advice
```text
================================================================================
ATTENDANCE AUDIT FOR STUDENT: 26BCE1003
================================================================================
Course: CSE1001 | Attended: 20/30 (66.67%) | Status: DEBARRED (<75%)
  Advice: CRITICAL: Below 75%! Must attend next 10 consecutive class(es) to regain eligibility.
--------------------------------------------------------------------------------
Course: PHY1001 | Attended: 20/24 (83.33%) | Status: ELIGIBLE
  Advice: Safe (83.33%). You can afford to miss up to 2 upcoming class(es) safely.
--------------------------------------------------------------------------------
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.