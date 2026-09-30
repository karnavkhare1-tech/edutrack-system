"""Unit tests for EduTrack input validation logic."""

import unittest
from edutrack.utils.validators import (
    validate_reg_no,
    validate_email,
    validate_course_code,
    validate_score,
    validate_credits,
    validate_non_empty_string,
)
from edutrack.utils.exceptions import ValidationError


class TestValidators(unittest.TestCase):
    """Test suite for validators and sanitizers."""

    def test_valid_reg_no(self):
        self.assertEqual(validate_reg_no("26bce1001"), "26BCE1001")
        self.assertEqual(validate_reg_no("23BCSE045"), "23BCSE045")

    def test_invalid_reg_no(self):
        with self.assertRaises(ValidationError):
            validate_reg_no("INVALID123")
        with self.assertRaises(ValidationError):
            validate_reg_no("261001")

    def test_valid_email(self):
        self.assertEqual(validate_email("student@vit.ac.in"), "student@vit.ac.in")

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            validate_email("not-an-email")

    def test_course_code_validation(self):
        self.assertEqual(validate_course_code("cse1001"), "CSE1001")
        with self.assertRaises(ValidationError):
            validate_course_code("CS1")

    def test_score_boundaries(self):
        self.assertEqual(validate_score("25.5", 30.0), 25.5)
        with self.assertRaises(ValidationError):
            validate_score(35.0, 30.0)
        with self.assertRaises(ValidationError):
            validate_score(-5.0, 30.0)

    def test_credits_boundaries(self):
        self.assertEqual(validate_credits(4), 4)
        with self.assertRaises(ValidationError):
            validate_credits(0)
        with self.assertRaises(ValidationError):
            validate_credits(6)

    def test_non_empty_string(self):
        self.assertEqual(validate_non_empty_string("  Data Structures  "), "Data Structures")
        with self.assertRaises(ValidationError):
            validate_non_empty_string("   ")


if __name__ == "__main__":
    unittest.main()
