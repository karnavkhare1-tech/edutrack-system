"""Attendance service managing session attendance logging and 75% rule compliance.

Tracks class attendance, calculates attendance percentages, detects debarred
status, and offers predictive recovery advice.
"""

from typing import Dict, List, Tuple, Any
from ..models import Student, CourseRecord
from ..utils.exceptions import AttendanceRecordError, StudentNotFoundError, CourseNotFoundError
from ..config import MIN_ATTENDANCE_PERCENTAGE


class AttendanceService:
    """Business logic service for student attendance."""

    def __init__(self, students_map: Dict[str, Student]):
        self._students = students_map

    def log_student_attendance(
        self,
        reg_no: str,
        course_code: str,
        attended: int,
        total: int,
    ) -> CourseRecord:
        """Update cumulative attendance for a student in a course."""
        reg_clean = reg_no.strip().upper()
        if reg_clean not in self._students:
            raise StudentNotFoundError(f"Student '{reg_clean}' not found.")

        student = self._students[reg_clean]
        code_clean = course_code.strip().upper()
        if code_clean not in student.courses:
            raise CourseNotFoundError(f"Student '{reg_clean}' is not enrolled in course '{code_clean}'.")

        if attended < 0 or total < 0:
            raise AttendanceRecordError("Attended and total classes cannot be negative.")
        if attended > total:
            raise AttendanceRecordError(
                f"Attended classes ({attended}) cannot exceed total conducted classes ({total})."
            )

        student.update_attendance(code_clean, attended, total)
        return student.courses[code_clean]

    def record_session(
        self,
        course_code: str,
        present_reg_nos: List[str],
    ) -> Dict[str, bool]:
        """Record attendance for a single class session across all enrolled students."""
        code_clean = course_code.strip().upper()
        present_set = {r.strip().upper() for r in present_reg_nos}
        results = {}

        for student in self._students.values():
            if code_clean in student.courses:
                rec = student.courses[code_clean]
                rec.total_classes += 1
                if student.reg_no in present_set:
                    rec.attended_classes += 1
                    results[student.reg_no] = True
                else:
                    results[student.reg_no] = False

        return results

    def get_debarred_students(self, course_code: str = "") -> List[Tuple[Student, str, CourseRecord]]:
        """Identify all students whose attendance is below MIN_ATTENDANCE_PERCENTAGE (75%)."""
        debarred = []
        code_filter = course_code.strip().upper() if course_code else None

        for student in self._students.values():
            for code, rec in student.courses.items():
                if code_filter and code != code_filter:
                    continue
                if rec.is_attendance_debarred:
                    debarred.append((student, code, rec))

        return debarred

    def get_student_summary(self, reg_no: str) -> List[Dict[str, Any]]:
        """Return comprehensive attendance status for all courses of a student."""
        reg_clean = reg_no.strip().upper()
        if reg_clean not in self._students:
            raise StudentNotFoundError(f"Student '{reg_clean}' not found.")

        student = self._students[reg_clean]
        summary = []
        for code, rec in student.courses.items():
            summary.append({
                "course_code": code,
                "attended": rec.attended_classes,
                "total": rec.total_classes,
                "percentage": rec.attendance_percentage,
                "is_debarred": rec.is_attendance_debarred,
                "advice": rec.attendance_advice(),
            })
        return summary
