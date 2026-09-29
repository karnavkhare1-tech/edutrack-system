"""Unit tests for EduTrack service layer."""

import unittest
from edutrack.services import StudentService, CourseService, AttendanceService, AnalyticsService
from edutrack.models import Student, Course
from edutrack.utils.exceptions import (
    StudentNotFoundError,
    CourseNotFoundError,
    DuplicateRecordError,
    AttendanceRecordError,
)


class TestServices(unittest.TestCase):
    """Test suite for Student, Course, Attendance, and Analytics services."""

    def setUp(self):
        self.students = {}
        self.courses = {}
        self.student_service = StudentService(self.students)
        self.course_service = CourseService(self.courses, self.students)
        self.attendance_service = AttendanceService(self.students)
        self.analytics_service = AnalyticsService(self.students, self.courses)

        # Setup initial course
        self.course_service.add_course("CSE1001", "Python Programming", 4, "Dr. Ramesh", "A1", 60)

    def test_student_crud_operations(self):
        s = self.student_service.add_student("24BCE1001", "Kavya Sharma", "kavya@vit.ac.in", "BCE", 1)
        self.assertIn("24BCE1001", self.students)
        self.assertEqual(s.name, "Kavya Sharma")

        # Duplicate check
        with self.assertRaises(DuplicateRecordError):
            self.student_service.add_student("24BCE1001", "Another Name", "another@vit.ac.in", "BCE", 1)

        # Get existing
        fetched = self.student_service.get_student("24BCE1001")
        self.assertEqual(fetched.name, "Kavya Sharma")

        # Search
        results = self.student_service.search("Kavya")
        self.assertEqual(len(results), 1)

        # Update
        self.student_service.update_student("24BCE1001", semester=2)
        self.assertEqual(self.students["24BCE1001"].semester, 2)

        # Delete
        self.student_service.delete_student("24BCE1001")
        self.assertNotIn("24BCE1001", self.students)

    def test_course_enrollment_and_drop(self):
        self.student_service.add_student("24BCE1002", "Dev Patel", "dev@vit.ac.in", "BCE", 1)
        self.course_service.enroll_student("24BCE1002", "CSE1001")

        enrolled = self.course_service.get_enrolled_students("CSE1001")
        self.assertEqual(len(enrolled), 1)
        self.assertEqual(enrolled[0].reg_no, "24BCE1002")

        # Drop student
        dropped = self.course_service.drop_student("24BCE1002", "CSE1001")
        self.assertTrue(dropped)
        self.assertEqual(len(self.course_service.get_enrolled_students("CSE1001")), 0)

    def test_attendance_logging_and_debarment(self):
        self.student_service.add_student("24BCE1003", "Rahul Roy", "rahul@vit.ac.in", "BCE", 1)
        self.course_service.enroll_student("24BCE1003", "CSE1001")

        # Negative / invalid attendance checks
        with self.assertRaises(AttendanceRecordError):
            self.attendance_service.log_student_attendance("24BCE1003", "CSE1001", attended=35, total=30)

        # Valid update with < 75%
        rec = self.attendance_service.log_student_attendance("24BCE1003", "CSE1001", attended=20, total=30)
        self.assertTrue(rec.is_attendance_debarred)

        debarred_list = self.attendance_service.get_debarred_students("CSE1001")
        self.assertEqual(len(debarred_list), 1)
        self.assertEqual(debarred_list[0][0].reg_no, "24BCE1003")

    def test_analytics_and_transcript_generation(self):
        self.student_service.add_student("24BCE1004", "Meera Sen", "meera@vit.ac.in", "BCE", 1)
        self.course_service.enroll_student("24BCE1004", "CSE1001")

        # Set attendance safe
        self.attendance_service.log_student_attendance("24BCE1004", "CSE1001", attended=28, total=30)

        # Record marks
        marks = self.analytics_service.record_student_marks(
            "24BCE1004", "CSE1001", quiz=10.0, assignment=19.0, midterm=28.0, final=38.0
        )
        self.assertEqual(marks["quiz"], 10.0)

        transcript = self.analytics_service.generate_student_transcript("24BCE1004")
        self.assertEqual(transcript["reg_no"], "24BCE1004")
        self.assertEqual(transcript["total_credits"], 4)
        self.assertEqual(transcript["gpa"], 10.0)  # Total 95 -> S Grade (10 GP)


if __name__ == "__main__":
    unittest.main()
