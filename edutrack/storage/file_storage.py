"""File storage manager for EduTrack.

Provides JSON persistence for domain entities (Students, Courses, Faculty)
and CSV export facilities for academic reports.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from ..config import STORAGE_FILE, REPORTS_DIR
from ..models import Student, Course, Faculty


class DataStorage:
    """Handles read/write operations for application state."""

    def __init__(self, filepath: Path = STORAGE_FILE):
        self.filepath = filepath
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file. Returns empty structure if file does not exist."""
        if not self.filepath.exists():
            return {"students": {}, "courses": {}, "faculty": {}}

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
                return {
                    "students": raw.get("students", {}),
                    "courses": raw.get("courses", {}),
                    "faculty": raw.get("faculty", {}),
                }
        except (json.JSONDecodeError, IOError) as err:
            print(f"[Warning] Failed to read {self.filepath}: {err}. Starting with clean state.")
            return {"students": {}, "courses": {}, "faculty": {}}

    def save_data(
        self,
        students: Dict[str, Student],
        courses: Dict[str, Course],
        faculty: Dict[str, Faculty],
    ) -> bool:
        """Atomically persist application state into JSON storage."""
        payload = {
            "students": {reg: s.to_dict() for reg, s in students.items()},
            "courses": {code: c.to_dict() for code, c in courses.items()},
            "faculty": {eid: f.to_dict() for eid, f in faculty.items()},
        }

        temp_path = self.filepath.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            temp_path.replace(self.filepath)
            return True
        except IOError as err:
            print(f"[Error] Failed to save state to {self.filepath}: {err}")
            if temp_path.exists():
                temp_path.unlink()
            return False

    def export_students_csv(
        self,
        students: List[Student],
        course_catalog: Dict[str, Course],
        filename: str = "students_report.csv",
    ) -> Path:
        """Export student summary and GPA to a CSV spreadsheet."""
        target_path = REPORTS_DIR / filename
        fieldnames = ["RegNo", "Name", "Branch", "Semester", "Email", "EnrolledCourses", "GPA"]

        with open(target_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for s in students:
                writer.writerow({
                    "RegNo": s.reg_no,
                    "Name": s.name,
                    "Branch": s.branch,
                    "Semester": s.semester,
                    "Email": s.email,
                    "EnrolledCourses": "; ".join(s.courses.keys()),
                    "GPA": s.calculate_gpa(course_catalog),
                })
        return target_path

    def export_attendance_csv(
        self,
        students: List[Student],
        filename: str = "attendance_summary.csv",
    ) -> Path:
        """Export comprehensive attendance audit across all enrolled courses to CSV."""
        target_path = REPORTS_DIR / filename
        fieldnames = [
            "RegNo",
            "StudentName",
            "CourseCode",
            "AttendedClasses",
            "TotalClasses",
            "AttendancePercentage",
            "DebarredStatus",
        ]

        with open(target_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for s in students:
                for c_code, rec in s.courses.items():
                    writer.writerow({
                        "RegNo": s.reg_no,
                        "StudentName": s.name,
                        "CourseCode": c_code,
                        "AttendedClasses": rec.attended_classes,
                        "TotalClasses": rec.total_classes,
                        "AttendancePercentage": f"{rec.attendance_percentage}%",
                        "DebarredStatus": "DEBARRED (<75%)" if rec.is_attendance_debarred else "ELIGIBLE",
                    })
        return target_path
