"""Input validation functions for EduTrack system.

Uses regular expressions and logical checks to sanitize and validate
all user inputs prior to business logic execution.
"""

import re
from .exceptions import ValidationError


def validate_reg_no(reg_no: str) -> str:
    """Validate university registration number format (e.g., 24BCE1001).

    Pattern: 2 digits (year) + 2 to 4 letters (dept) + 3 to 5 digits (roll).
    """
    if not isinstance(reg_no, str):
        raise ValidationError("Registration number must be a string.")
    cleaned = reg_no.strip().upper()
    pattern = r"^[0-9]{2}[A-Z]{2,4}[0-9]{3,5}$"
    if not re.match(pattern, cleaned):
        raise ValidationError(
            f"Invalid Registration Number '{reg_no}'. "
            "Expected format: 2 digits year + 2-4 branch letters + 3-5 digits (e.g., 24BCE1001)."
        )
    return cleaned


def validate_email(email: str) -> str:
    """Validate student or faculty email address."""
    if not isinstance(email, str):
        raise ValidationError("Email must be a string.")
    cleaned = email.strip().lower()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, cleaned):
        raise ValidationError(f"Invalid email address '{email}'.")
    return cleaned


def validate_course_code(code: str) -> str:
    """Validate university course code (e.g., CSE1001, MAT2001, PHY1002).

    Pattern: 3 to 4 uppercase letters followed by 4 digits.
    """
    if not isinstance(code, str):
        raise ValidationError("Course code must be a string.")
    cleaned = code.strip().upper()
    pattern = r"^[A-Z]{3,4}[0-9]{4}$"
    if not re.match(pattern, cleaned):
        raise ValidationError(
            f"Invalid Course Code '{code}'. "
            "Expected format: 3-4 letters followed by 4 digits (e.g., CSE1001)."
        )
    return cleaned


def validate_score(score: float, max_score: float = 100.0, assessment_name: str = "Assessment") -> float:
    """Validate numerical assessment score."""
    try:
        val = float(score)
    except (ValueError, TypeError):
        raise ValidationError(f"{assessment_name} score must be a valid number.")

    if val < 0.0 or val > max_score:
        raise ValidationError(
            f"{assessment_name} score ({val}) must be between 0.0 and {max_score}."
        )
    return round(val, 2)


def validate_credits(credits_val: int) -> int:
    """Validate course credits (typically 1 to 5 for university courses)."""
    try:
        c = int(credits_val)
    except (ValueError, TypeError):
        raise ValidationError("Credits must be an integer.")

    if c < 1 or c > 5:
        raise ValidationError(f"Course credits must be between 1 and 5. Received: {c}")
    return c


def validate_non_empty_string(value: str, field_name: str = "Field") -> str:
    """Validate that a string is non-empty and non-whitespace."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty.")
    return value.strip()
