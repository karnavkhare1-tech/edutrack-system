"""Course service managing course catalog and student enrollments.

Provides CRUD functionality and enrollment workflows for courses.
"""

from typing import Dict, List, Optional
from ..models import Course, Student
from ..utils.exceptions import CourseNotFoundError, DuplicateRecordError, ValidationError
from ..utils.validators import validate_course_code, validate_credits, validate_non_empty_string


class CourseService:
    """Business logic service for course operations."""

    def __init__(self, courses_map: Dict[str, Course], students_map: Dict[str, Student]):
        self._courses = courses_map
        self._students = students_map

    def add_course(
        self,
        code: str,
        title: str,
        credits: int,
        faculty_name: str = "TBA",
        slot: str = "A1",
        max_capacity: int = 60,
    ) -> Course:
        """Create and register a new academic course."""
        valid_code = validate_course_code(code)
        valid_title = validate_non_empty_string(title, "Course title")
        valid_credits = validate_credits(credits)

        if valid_code in self._courses:
            raise DuplicateRecordError(f"Course code '{valid_code}' already exists in catalog.")

        course = Course(
            code=valid_code,
            title=valid_title,
            credits=valid_credits,
            faculty_name=faculty_name,
            slot=slot,
            max_capacity=max_capacity,
        )
        self._courses[valid_code] = course
        return course

    def get_course(self, code: str) -> Course:
        """Fetch course by code or raise CourseNotFoundError."""
        cleaned = code.strip().upper()
        if cleaned not in self._courses:
            raise CourseNotFoundError(f"Course '{cleaned}' does not exist in catalog.")
        return self._courses[cleaned]

    def update_course(
        self,
        code: str,
        title: Optional[str] = None,
        credits: Optional[int] = None,
        faculty_name: Optional[str] = None,
        slot: Optional[str] = None,
    ) -> Course:
        """Update existing course metadata."""
        course = self.get_course(code)
        if title is not None:
            course.title = validate_non_empty_string(title, "Course title")
        if credits is not None:
            course.credits = validate_credits(credits)
        if faculty_name is not None:
            course.faculty_name = faculty_name.strip()
        if slot is not None:
            course.slot = slot.strip().upper()
        return course

    def delete_course(self, code: str) -> bool:
        """Delete course from catalog and cascade drop from students."""
        cleaned = code.strip().upper()
        if cleaned not in self._courses:
            raise CourseNotFoundError(f"Cannot delete: Course '{cleaned}' not found.")

        # Drop from enrolled students
        for student in self._students.values():
            student.drop(cleaned)

        del self._courses[cleaned]
        return True

    def list_all(self) -> List[Course]:
        """Return list of all registered courses."""
        return sorted(self._courses.values(), key=lambda c: c.code)

    def enroll_student(self, reg_no: str, course_code: str) -> None:
        """Enroll a student into a course if seat capacity permits."""
        valid_code = validate_course_code(course_code)
        course = self.get_course(valid_code)

        reg_clean = reg_no.strip().upper()
        if reg_clean not in self._students:
            raise ValidationError(f"Student '{reg_clean}' must be registered before enrolling.")
        student = self._students[reg_clean]

        # Check existing enrollment
        if valid_code in student.courses:
            raise DuplicateRecordError(f"Student '{reg_clean}' is already enrolled in '{valid_code}'.")

        # Check capacity
        enrolled_count = len(self.get_enrolled_students(valid_code))
        if enrolled_count >= course.max_capacity:
            raise ValidationError(f"Course '{valid_code}' has reached its maximum capacity of {course.max_capacity}.")

        student.enroll(valid_code)

    def drop_student(self, reg_no: str, course_code: str) -> bool:
        """Drop a student from a course."""
        valid_code = validate_course_code(course_code)
        reg_clean = reg_no.strip().upper()
        if reg_clean not in self._students:
            raise ValidationError(f"Student '{reg_clean}' not found.")
        return self._students[reg_clean].drop(valid_code)

    def get_enrolled_students(self, course_code: str) -> List[Student]:
        """Get all students registered in a course."""
        code = course_code.strip().upper()
        return [s for s in self._students.values() if code in s.courses]
