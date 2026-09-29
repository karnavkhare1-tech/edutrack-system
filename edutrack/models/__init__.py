"""Models package initialization."""

from .person import Person, Faculty
from .course import Course
from .student import Student, CourseRecord

__all__ = ["Person", "Faculty", "Course", "Student", "CourseRecord"]
