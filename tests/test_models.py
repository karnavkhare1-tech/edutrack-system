"""Unit tests for EduTrack domain models."""

import unittest
from edutrack.models.person import Person, Faculty
from edutrack.models.course import Course
from edutrack.models.student import Student, CourseRecord


class TestDomainModels(unittest.TestCase):
    """Test suite for OOP domain models."""

    def test_person_and_faculty_inheritance(self):
        p = Person("John Doe", "john@example.com", "1234567890")
        self.assertEqual(p.get_role(), "Person")
        self.assertEqual(p.name, "John Doe")

        f = Faculty("FAC01", "Dr. Alan Turing", "alan@vit.ac.in", "CSE")
        self.assertEqual(f.get_role(), "Faculty")
        self.assertEqual(f.emp_id, "FAC01")
        self.assertEqual(f.department, "CSE")
        self.assertIn("Alan Turing", str(f))

    def test_course_creation_and_serialization(self):
        c = Course("CSE1001", "Python Programming", 4, "Dr. Ramesh", "A1", 60)
        self.assertEqual(c.code, "CSE1001")
        self.assertEqual(c.credits, 4)

        data = c.to_dict()
        reconstructed = Course.from_dict(data)
        self.assertEqual(reconstructed.code, c.code)
        self.assertEqual(reconstructed.credits, c.credits)

    def test_course_record_attendance_and_grades(self):
        rec = CourseRecord("CSE1001", attended_classes=24, total_classes=30)
        self.assertEqual(rec.attendance_percentage, 80.0)
        self.assertFalse(rec.is_attendance_debarred)

        # Below 75%
        rec.attended_classes = 20
        self.assertEqual(rec.attendance_percentage, 66.67)
        self.assertTrue(rec.is_attendance_debarred)
        self.assertEqual(rec.grade_letter, "F (Debarred)")
        self.assertEqual(rec.grade_point, 0)
        self.assertEqual(rec.status, "DEBARRED")

    def test_student_gpa_calculation(self):
        s = Student("26BCE1001", "Alice", "alice@vit.ac.in", "BCE", 1)
        s.enroll("CSE1001")
        s.enroll("MAT1001")

        # 30/30 attendance for both
        s.update_attendance("CSE1001", 30, 30)
        s.update_attendance("MAT1001", 30, 30)

        # Marks: CSE1001 = 95 (S -> 10 GP), MAT1001 = 85 (A -> 9 GP)
        s.update_marks("CSE1001", quiz=10, assignment=20, midterm=28, final=37) # 95
        s.update_marks("MAT1001", quiz=8, assignment=18, midterm=25, final=34) # 85

        catalog = {
            "CSE1001": Course("CSE1001", "Python", 4),
            "MAT1001": Course("MAT1001", "Math", 4),
        }

        # Weighted GPA = (10*4 + 9*4) / 8 = 76 / 8 = 9.5
        gpa = s.calculate_gpa(catalog)
        self.assertEqual(gpa, 9.5)


if __name__ == "__main__":
    unittest.main()
