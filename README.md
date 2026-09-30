# EduTrack

**Academic Performance & Attendance Monitoring System**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)](tests/)

> A clean, modular, Object-Oriented Academic Performance and Attendance Management System designed to help university students and faculty track course enrollments, enforce the mandatory 75% attendance rule, calculate credit-weighted GPAs, and generate institutional analytics.

---

## 📖 Overview
In academic environments, maintaining attendance above the mandatory 75% threshold and tracking multi-component evaluation scores (quizzes, assignments, midterms, and finals) across courses with varying credit weightages is challenging. 

**EduTrack** provides an automated, reliable, and user-friendly platform tailored for undergraduate university workflows. Built using fundamental Python concepts (Object-Oriented Programming, modular layered architecture, data serialization, and custom exception handling), EduTrack ensures students avoid examination debarment while offering faculty actionable course insights.

---

## ✨ Key Features

### 1. Student & Course Management
- **Student Profile Management**: Register, search, view, update, and remove students with automated registration number and email format validation.
- **Course Offering Catalog**: Configure course codes, titles, credits (1 to 5), instructor details, slots, and seat capacities.
- **Seat Enrollment Engine**: Enroll and drop courses with capacity validation checks.

### 2. Attendance Tracking & 75% Rule Compliance
- **Session Attendance Marking**: Quick bulk session marking (present/absent) for enrolled students.
- **Cumulative Attendance Audit**: View attendance percentages and real-time eligibility status.
- **Predictive Margin Advice**:
  - If `< 75%`: Calculates exact number of consecutive upcoming classes a student must attend to regain eligibility.
  - If `≥ 75%`: Calculates the safe attendance buffer (classes that can be missed without falling below 75%).
- **Debarred Registry**: Instantly lists all students debarred from examinations across courses.

### 3. Academic Evaluation & Analytics
- **Continuous Internal & Final Marks**: Track quizzes (10), assignments (20), midterms (30), and final examinations (40).
- **10-Point Scale Letter Grading**: Automated mapping to S (≥90), A (≥80), B (≥70), C (≥60), D (≥50), E (≥40), and F (<40 or Debarred).
- **Weighted GPA Calculator**: Accurately computes Semester Grade Point Average (SGPA):
  $$\text{GPA} = \frac{\sum (\text{Grade Point}_i \times \text{Credits}_i)}{\sum \text{Credits}_i}$$
- **Course Analytics**: Computes course average score, highest/lowest marks, pass percentage, and grade distribution histograms.
- **Dean's Honor Roll**: Live leaderboard of top rankers sorted by GPA.

### 4. Data Persistence & CSV Exports
- **Atomic JSON Storage**: Safely persists state across sessions in `data/edutrack_data.json`.
- **CSV Data Export**: One-click generation of student GPA summaries and comprehensive attendance audits in `reports/`.

---

## 🛠️ Technologies & Tools Used
- **Core Language**: Python 3.8+ (Zero external dependencies; uses Python Standard Library).
- **Core Concepts Applied**:
  - **OOP Principles**: Classes, Inheritance (`Person` $\rightarrow$ `Student`, `Faculty`), Encapsulation (`@property` getters/setters), and Polymorphism.
  - **Data Structures**: Dictionaries, Lists, Tuples, Sets for high-efficiency in-memory state indexing.
  - **File I/O**: `json` serialization with safe write mechanisms and `csv` for spreadsheet report generation.
  - **Regular Expressions**: `re` module for strict format validation (Reg No: e.g. `24BCE1001`, Email, Course Codes).
  - **Custom Exception Handling**: Hierarchical domain-specific exceptions inheriting from `EduTrackException`.
  - **Unit Testing**: Python's built-in `unittest` framework.

---

## 📁 Project Structure
```text
edutrack-system/
├── edutrack/
│   ├── __init__.py               # Package initializer
│   ├── config.py                 # Academic constants, thresholds & paths
│   ├── data_seed.py              # Sample dataset generator
│   ├── models/                   # OOP Domain Models
│   │   ├── __init__.py
│   │   ├── person.py             # Base Person and Faculty classes
│   │   ├── student.py            # Student and CourseRecord models
│   │   └── course.py             # Academic Course model
│   ├── services/                 # Layered Business Logic
│   │   ├── __init__.py
│   │   ├── student_service.py    # Student CRUD and search logic
│   │   ├── course_service.py     # Course catalog & enrollment logic
│   │   ├── attendance_service.py # Attendance & 75% rule audit
│   │   └── analytics_service.py  # Marks, SGPA & course statistics
│   ├── storage/                  # Data Persistence Layer
│   │   ├── __init__.py
│   │   └── file_storage.py       # JSON storage & CSV export utilities
│   ├── utils/                    # Shared Utilities & Validations
│   │   ├── __init__.py
│   │   ├── exceptions.py         # Custom application exceptions
│   │   └── validators.py         # RegEx sanitizers and validators
│   └── cli/                      # Interactive User Interface
│       ├── __init__.py
│       └── menu.py               # Formatted CLI menu and controllers
├── tests/                        # Automated Unit Testing Suite
│   ├── __init__.py
│   ├── test_models.py            # Domain model & GPA calculation tests
│   ├── test_services.py          # Business logic & workflow tests
│   └── test_validators.py        # Input validation boundary tests
├── data/                         # Persistent JSON storage directory
│   └── edutrack_data.json
├── reports/                      # Exported CSV spreadsheets
│   ├── students_report.csv
│   └── attendance_summary.csv
├── main.py                       # Main application entry point
├── demo.py                       # Automated end-to-end demo runner
├── statement.md                  # Project Statement (Rubric Item 5.2)
├── PROJECT_REPORT.md             # Complete 15-Section Project Report (Rubric Item 6)
├── .gitignore                    # Standard Git exclusions
└── README.md                     # Project overview and instructions
```

---

## 🚀 Installation & Running Instructions

### Prerequisites
- Python 3.8 or higher installed on your machine.
- No third-party packages or virtual environment activation required!

### Step 1: Clone or Navigate to the Project Folder
```bash
git clone https://github.com/<your-username>/edutrack.git
cd edutrack
```

### Step 2: Run the Interactive Application
```bash
python main.py
```

### Step 3: Run the Automated Demo Script
To view an end-to-end demonstration and generate sample CSV reports immediately:
```bash
python demo.py
```

---

## 🧪 Instructions for Testing

The system includes a comprehensive unit testing suite covering models, service workflows, edge cases (e.g., negative attendance, scores exceeding 100, duplicate registrations), and GPA calculations.

Run the test suite via Python's `unittest` module:
```bash
python -m unittest discover -s tests
```

### Test Suite Output:
```text
Ran 16 tests in 0.002s

OK
```

---

## 💻 Sample CLI Outputs & Walkthrough

### 1. Main Application Menu
```text
=================================================================
       EDUTRACK - ACADEMIC & ATTENDANCE MANAGEMENT SYSTEM
        Empowering Student Success & Institutional Insights
=================================================================
 Registered Students: 5 | Active Courses: 4
=================================================================
1. Student Management (Add, View, Update, Delete)
2. Course Catalog & Enrollments
3. Attendance Tracking & 75% Rule Compliance
4. Academic Marks, GPA & Performance Analytics
5. Export Reports & Data Management (CSV Export)
0. Save & Exit
-----------------------------------------------------------------
Select an option [0-5]:
```

### 2. Student Academic Transcript & GPA
```text
==========================================================================================
ACADEMIC TRANSCRIPT: Aarav Sharma (24BCE1001)
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

### 3. Attendance Margin & Recovery Advice
```text
================================================================================
ATTENDANCE AUDIT FOR STUDENT: 24BCE1003
================================================================================
Course: CSE1001 | Attended: 20/30 (66.67%) | Status: DEBARRED (<75%)
  Advice: CRITICAL: Below 75%! Must attend next 10 consecutive class(es) to regain eligibility.
--------------------------------------------------------------------------------
Course: PHY1001 | Attended: 20/24 (83.33%) | Status: ELIGIBLE
  Advice: Safe (83.33%). You can afford to miss up to 2 upcoming class(es) safely.
--------------------------------------------------------------------------------
```

---

## 📄 License
This project is open-source and developed for academic evaluation under the MIT License.
#   V i t y a r t h i - p r o j e c t 
 
 