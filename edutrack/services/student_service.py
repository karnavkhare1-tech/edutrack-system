"""Student service managing student records and operations.

Provides CRUD functionality, search/filtering, and validation for students.
"""

from typing import Dict, List, Optional
from ..models import Student
from ..utils.exceptions import StudentNotFoundError, DuplicateRecordError
from ..utils.validators import validate_reg_no, validate_email, validate_non_empty_string


class StudentService:
    """Business logic service for managing students."""

    def __init__(self, students_map: Dict[str, Student]):
        self._students = students_map

    def add_student(
        self,
        reg_no: str,
        name: str,
        email: str,
        branch: str,
        semester: int = 1,
        phone: str = "",
    ) -> Student:
        """Register a new student with strict validation."""
        valid_reg = validate_reg_no(reg_no)
        valid_name = validate_non_empty_string(name, "Student name")
        valid_email = validate_email(email)
        valid_branch = validate_non_empty_string(branch, "Branch").upper()

        if valid_reg in self._students:
            raise DuplicateRecordError(f"Student with Registration Number '{valid_reg}' already exists.")

        student = Student(
            reg_no=valid_reg,
            name=valid_name,
            email=valid_email,
            branch=valid_branch,
            semester=semester,
            phone=phone,
        )
        self._students[valid_reg] = student
        return student

    def get_student(self, reg_no: str) -> Student:
        """Retrieve student by registration number or raise StudentNotFoundError."""
        cleaned = reg_no.strip().upper()
        if cleaned not in self._students:
            raise StudentNotFoundError(f"Student with Registration Number '{cleaned}' was not found.")
        return self._students[cleaned]

    def update_student(
        self,
        reg_no: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        branch: Optional[str] = None,
        semester: Optional[int] = None,
        phone: Optional[str] = None,
    ) -> Student:
        """Update existing student profile details."""
        student = self.get_student(reg_no)
        if name is not None:
            student.name = validate_non_empty_string(name, "Name")
        if email is not None:
            student.email = validate_email(email)
        if branch is not None:
            student.branch = validate_non_empty_string(branch, "Branch").upper()
        if semester is not None:
            student.semester = int(semester)
        if phone is not None:
            student.phone = phone.strip()
        return student

    def delete_student(self, reg_no: str) -> bool:
        """Remove a student from the system."""
        cleaned = reg_no.strip().upper()
        if cleaned in self._students:
            del self._students[cleaned]
            return True
        raise StudentNotFoundError(f"Cannot delete: Student '{cleaned}' not found.")

    def list_all(self) -> List[Student]:
        """Return all registered students sorted by registration number."""
        return sorted(self._students.values(), key=lambda s: s.reg_no)

    def filter_by_branch(self, branch: str) -> List[Student]:
        """Filter students by department branch."""
        b = branch.strip().upper()
        return [s for s in self._students.values() if s.branch == b]

    def search(self, query: str) -> List[Student]:
        """Search students matching name or registration number query."""
        q = query.strip().upper()
        return [
            s for s in self._students.values()
            if q in s.reg_no or q in s.name.upper()
        ]
