"""Sample dataset generator for EduTrack.

Provides realistic baseline seed data for demonstration and testing.
"""

from typing import Dict
from .models import Student, Course, Faculty


def generate_seed_data():
    """Generates initial sample courses, faculty, and students with realistic marks/attendance."""
    # 1. Faculty
    faculty: Dict[str, Faculty] = {
        "FAC101": Faculty("FAC101", "Dr. Ramesh Kumar", "ramesh.k@vit.ac.in", "Computer Science"),
        "FAC102": Faculty("FAC102", "Prof. Ananya Sen", "ananya.s@vit.ac.in", "Mathematics"),
        "FAC103": Faculty("FAC103", "Dr. Priya Sundaram", "priya.s@vit.ac.in", "Physics"),
    }

    # 2. Courses
    courses: Dict[str, Course] = {
        "CSE1001": Course("CSE1001", "Problem Solving and Programming with Python", 4, "Dr. Ramesh Kumar", "A1+TA1", 60),
        "MAT1001": Course("MAT1001", "Calculus and Linear Algebra", 4, "Prof. Ananya Sen", "B1+TB1", 60),
        "PHY1001": Course("PHY1001", "Engineering Physics", 3, "Dr. Priya Sundaram", "C1+TC1", 50),
        "ENG1001": Course("ENG1001", "Technical English Communication", 2, "Dr. Ramesh Kumar", "D1", 40),
    }

    # 3. Students
    students: Dict[str, Student] = {
        "24BCE1001": Student("24BCE1001", "Aarav Sharma", "aarav.s2024@vitstudent.ac.in", "BCE", 1, "9876543210"),
        "24BCE1002": Student("24BCE1002", "Diya Patel", "diya.p2024@vitstudent.ac.in", "BCE", 1, "9876543211"),
        "24BCE1003": Student("24BCE1003", "Rohan Verma", "rohan.v2024@vitstudent.ac.in", "BCE", 1, "9876543212"),
        "24BCE1004": Student("24BCE1004", "Sneha Iyer", "sneha.i2024@vitstudent.ac.in", "BCE", 1, "9876543213"),
        "24BCE1005": Student("24BCE1005", "Vikram Nair", "vikram.n2024@vitstudent.ac.in", "BCE", 1, "9876543214"),
    }

    # Setup Course Enrollments, Attendance & Marks
    # Student 1: High achiever
    s1 = students["24BCE1001"]
    for c in ["CSE1001", "MAT1001", "PHY1001"]:
        s1.enroll(c)
    s1.update_attendance("CSE1001", attended=28, total=30)  # 93.3%
    s1.update_marks("CSE1001", quiz=9.5, assignment=19.0, midterm=28.0, final=38.0) # Total 94.5 (S)
    s1.update_attendance("MAT1001", attended=27, total=30)  # 90.0%
    s1.update_marks("MAT1001", quiz=8.5, assignment=18.0, midterm=26.0, final=35.0) # Total 87.5 (A)
    s1.update_attendance("PHY1001", attended=22, total=24)  # 91.7%
    s1.update_marks("PHY1001", quiz=9.0, assignment=17.5, midterm=27.0, final=36.0) # Total 89.5 (A)

    # Student 2: Average with safe attendance
    s2 = students["24BCE1002"]
    for c in ["CSE1001", "MAT1001"]:
        s2.enroll(c)
    s2.update_attendance("CSE1001", attended=24, total=30)  # 80.0%
    s2.update_marks("CSE1001", quiz=7.0, assignment=15.0, midterm=22.0, final=30.0) # Total 74.0 (B)
    s2.update_attendance("MAT1001", attended=23, total=30)  # 76.7%
    s2.update_marks("MAT1001", quiz=6.5, assignment=14.0, midterm=20.0, final=28.0) # Total 68.5 (C)

    # Student 3: Low attendance (Debarred in CSE1001!)
    s3 = students["24BCE1003"]
    for c in ["CSE1001", "PHY1001"]:
        s3.enroll(c)
    s3.update_attendance("CSE1001", attended=20, total=30)  # 66.7% (<75% Debarred!)
    s3.update_marks("CSE1001", quiz=8.0, assignment=16.0, midterm=24.0, final=32.0)
    s3.update_attendance("PHY1001", attended=20, total=24)  # 83.3%
    s3.update_marks("PHY1001", quiz=7.5, assignment=15.0, midterm=21.0, final=29.0)

    # Student 4: High performer
    s4 = students["24BCE1004"]
    for c in ["CSE1001", "MAT1001", "PHY1001", "ENG1001"]:
        s4.enroll(c)
    s4.update_attendance("CSE1001", attended=29, total=30)  # 96.7%
    s4.update_marks("CSE1001", quiz=10.0, assignment=20.0, midterm=29.0, final=39.0) # Total 98.0 (S)
    s4.update_attendance("MAT1001", attended=28, total=30)
    s4.update_marks("MAT1001", quiz=9.0, assignment=19.0, midterm=27.5, final=37.0) # Total 92.5 (S)
    s4.update_attendance("PHY1001", attended=23, total=24)
    s4.update_marks("PHY1001", quiz=8.5, assignment=18.0, midterm=26.0, final=36.0) # Total 88.5 (A)
    s4.update_attendance("ENG1001", attended=18, total=20)
    s4.update_marks("ENG1001", quiz=9.0, assignment=18.5, midterm=28.0, final=37.0) # Total 92.5 (S)

    # Student 5: Near 75% boundary
    s5 = students["24BCE1005"]
    for c in ["MAT1001", "ENG1001"]:
        s5.enroll(c)
    s5.update_attendance("MAT1001", attended=22, total=30)  # 73.3% (<75% Debarred!)
    s5.update_marks("MAT1001", quiz=5.0, assignment=12.0, midterm=16.0, final=22.0)
    s5.update_attendance("ENG1001", attended=16, total=20)  # 80.0%
    s5.update_marks("ENG1001", quiz=7.0, assignment=14.0, midterm=22.0, final=28.0)

    return faculty, courses, students
