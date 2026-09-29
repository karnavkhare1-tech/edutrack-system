"""Utility package initialization."""

from .exceptions import (
    EduTrackException,
    StudentNotFoundError,
    CourseNotFoundError,
    DuplicateRecordError,
    ValidationError,
    AttendanceRecordError,
    InvalidScoreError,
)
from .validators import (
    validate_reg_no,
    validate_email,
    validate_course_code,
    validate_score,
    validate_credits,
    validate_non_empty_string,
)

__all__ = [
    "EduTrackException",
    "StudentNotFoundError",
    "CourseNotFoundError",
    "DuplicateRecordError",
    "ValidationError",
    "AttendanceRecordError",
    "InvalidScoreError",
    "validate_reg_no",
    "validate_email",
    "validate_course_code",
    "validate_score",
    "validate_credits",
    "validate_non_empty_string",
]
