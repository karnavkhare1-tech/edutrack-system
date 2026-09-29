"""Custom exception classes for EduTrack application.

Encapsulates application-specific error states for robust error handling.
"""


class EduTrackException(Exception):
    """Base exception for all EduTrack application errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(EduTrackException):
    """Raised when an input fails validation criteria."""
    pass


class StudentNotFoundError(EduTrackException):
    """Raised when a student cannot be found by their Registration Number."""
    pass


class CourseNotFoundError(EduTrackException):
    """Raised when a course cannot be found by its Course Code."""
    pass


class DuplicateRecordError(EduTrackException):
    """Raised when attempting to add an entity that already exists."""
    pass


class AttendanceRecordError(EduTrackException):
    """Raised when attendance logging contains logical contradictions."""
    pass


class InvalidScoreError(EduTrackException):
    """Raised when assessment marks exceed bounds or are invalid."""
    pass
