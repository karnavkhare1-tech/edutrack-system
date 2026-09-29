"""Student and CourseRecord domain models.

Encapsulates student information, course enrollments, attendance tracking,
and academic marks evaluation.
"""

from typing import Dict, Any, Optional
from .person import Person
from ..config import (
    MIN_ATTENDANCE_PERCENTAGE,
    GRADE_SCALE,
    ASSESSMENT_MAX_MARKS,
    TOTAL_MARKS,
)


class CourseRecord:
    """Holds academic progress for a single course enrollment."""

    def __init__(
        self,
        course_code: str,
        attended_classes: int = 0,
        total_classes: int = 0,
        marks: Optional[Dict[str, float]] = None,
    ):
        self.course_code = course_code.strip().upper()
        self.attended_classes = max(0, int(attended_classes))
        self.total_classes = max(0, int(total_classes))
        self.marks = marks if marks is not None else {
            "quiz": 0.0,
            "assignment": 0.0,
            "midterm": 0.0,
            "final": 0.0,
        }

    @property
    def attendance_percentage(self) -> float:
        """Calculate current attendance percentage."""
        if self.total_classes == 0:
            return 100.0  # No classes held yet, considered 100%
        return round((self.attended_classes / self.total_classes) * 100.0, 2)

    @property
    def is_attendance_debarred(self) -> bool:
        """Returns True if attendance falls below the mandatory 75% threshold."""
        if self.total_classes == 0:
            return False
        return self.attendance_percentage < MIN_ATTENDANCE_PERCENTAGE

    def attendance_advice(self) -> str:
        """Actionable advice on attendance margin or recovery to maintain 75%."""
        if self.total_classes == 0:
            return "No classes conducted yet."

        pct = self.attendance_percentage
        if pct < MIN_ATTENDANCE_PERCENTAGE:
            # Formula: (attended + x) / (total + x) >= 0.75
            # attended + x >= 0.75 * total + 0.75 * x
            # 0.25 * x >= 0.75 * total - attended
            # x >= (0.75 * total - attended) / 0.25 = 3 * total - 4 * attended
            needed = (3 * self.total_classes) - (4 * self.attended_classes)
            needed = max(0, needed)
            return f"CRITICAL: Below 75%! Must attend next {needed} consecutive class(es) to regain eligibility."
        else:
            # Formula: attended / (total + y) >= 0.75
            # attended >= 0.75 * total + 0.75 * y
            # 0.75 * y <= attended - 0.75 * total
            # y <= (attended - 0.75 * total) / 0.75 = (4 * attended - 3 * total) / 3
            margin = (4 * self.attended_classes - 3 * self.total_classes) // 3
            margin = max(0, margin)
            return f"Safe ({pct}%). You can afford to miss up to {margin} upcoming class(es) safely."

    @property
    def total_score(self) -> float:
        """Sum of all assessment marks out of 100."""
        return round(sum(self.marks.values()), 2)

    @property
    def grade_letter(self) -> str:
        """Determines academic letter grade (S, A, B, C, D, E, F)."""
        if self.is_attendance_debarred:
            return "F (Debarred)"
        tot = self.total_score
        for letter, min_score, _ in GRADE_SCALE:
            if tot >= min_score:
                return letter
        return "F"

    @property
    def grade_point(self) -> int:
        """Determines grade point (0-10) for GPA computation."""
        if self.is_attendance_debarred:
            return 0
        tot = self.total_score
        for _, min_score, gp in GRADE_SCALE:
            if tot >= min_score:
                return gp
        return 0

    @property
    def status(self) -> str:
        """Pass/Fail/Debarred status."""
        if self.is_attendance_debarred:
            return "DEBARRED"
        return "PASS" if self.grade_point >= 5 else "FAIL"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize course record to dictionary."""
        return {
            "course_code": self.course_code,
            "attended_classes": self.attended_classes,
            "total_classes": self.total_classes,
            "marks": self.marks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CourseRecord":
        """Deserialize from dictionary."""
        return cls(
            course_code=data["course_code"],
            attended_classes=data.get("attended_classes", 0),
            total_classes=data.get("total_classes", 0),
            marks=data.get("marks", {k: 0.0 for k in ASSESSMENT_MAX_MARKS}),
        )


class Student(Person):
    """Student class representing an enrolled university student."""

    def __init__(
        self,
        reg_no: str,
        name: str,
        email: str,
        branch: str,
        semester: int = 1,
        phone: str = "",
    ):
        super().__init__(name=name, email=email, phone=phone)
        self.reg_no = reg_no.strip().upper()
        self.branch = branch.strip().upper()
        self.semester = int(semester)
        self.courses: Dict[str, CourseRecord] = {}

    def get_role(self) -> str:
        return "Student"

    def enroll(self, course_code: str) -> None:
        """Enroll in a course by course code."""
        code = course_code.strip().upper()
        if code not in self.courses:
            self.courses[code] = CourseRecord(course_code=code)

    def drop(self, course_code: str) -> bool:
        """Drop an enrolled course."""
        code = course_code.strip().upper()
        if code in self.courses:
            del self.courses[code]
            return True
        return False

    def update_attendance(self, course_code: str, attended: int, total: int) -> None:
        """Update attendance record for a course."""
        code = course_code.strip().upper()
        if code not in self.courses:
            self.enroll(code)
        self.courses[code].attended_classes = attended
        self.courses[code].total_classes = total

    def update_marks(
        self,
        course_code: str,
        quiz: Optional[float] = None,
        assignment: Optional[float] = None,
        midterm: Optional[float] = None,
        final: Optional[float] = None,
    ) -> None:
        """Update assessment scores for a course."""
        code = course_code.strip().upper()
        if code not in self.courses:
            self.enroll(code)
        rec = self.courses[code]
        if quiz is not None:
            rec.marks["quiz"] = round(quiz, 2)
        if assignment is not None:
            rec.marks["assignment"] = round(assignment, 2)
        if midterm is not None:
            rec.marks["midterm"] = round(midterm, 2)
        if final is not None:
            rec.marks["final"] = round(final, 2)

    def calculate_gpa(self, course_catalog: Dict[str, Any]) -> float:
        """Calculate weighted Grade Point Average (GPA) using course credits.

        GPA = sum(grade_point * credits) / sum(credits)
        """
        if not self.courses:
            return 0.0

        total_credits = 0
        weighted_points = 0.0

        for code, record in self.courses.items():
            course = course_catalog.get(code)
            # Default to 3 credits if course metadata missing
            credits = course.credits if course else 3
            total_credits += credits
            weighted_points += record.grade_point * credits

        if total_credits == 0:
            return 0.0

        return round(weighted_points / total_credits, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize student to dictionary."""
        data = super().to_dict()
        data.update({
            "reg_no": self.reg_no,
            "branch": self.branch,
            "semester": self.semester,
            "courses": {k: v.to_dict() for k, v in self.courses.items()},
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Deserialize from dictionary."""
        student = cls(
            reg_no=data["reg_no"],
            name=data["name"],
            email=data["email"],
            branch=data["branch"],
            semester=data.get("semester", 1),
            phone=data.get("phone", ""),
        )
        courses_dict = data.get("courses", {})
        for code, c_data in courses_dict.items():
            student.courses[code] = CourseRecord.from_dict(c_data)
        return student

    def __str__(self) -> str:
        return f"Student [{self.reg_no}] {self.name} - {self.branch} (Sem {self.semester})"
