"""Analytics service for marks evaluation, GPA computation, and academic statistics.

Provides grade distribution analysis, class rankings, and academic performance metrics.
"""

from typing import Dict, List, Any, Optional
from ..models import Student, Course
from ..utils.exceptions import StudentNotFoundError, CourseNotFoundError, InvalidScoreError
from ..utils.validators import validate_score
from ..config import ASSESSMENT_MAX_MARKS, GRADE_SCALE


class AnalyticsService:
    """Business logic service for marks and academic performance analytics."""

    def __init__(self, students_map: Dict[str, Student], courses_map: Dict[str, Course]):
        self._students = students_map
        self._courses = courses_map

    def record_student_marks(
        self,
        reg_no: str,
        course_code: str,
        quiz: Optional[float] = None,
        assignment: Optional[float] = None,
        midterm: Optional[float] = None,
        final: Optional[float] = None,
    ) -> Dict[str, float]:
        """Record or update evaluation scores for a student in a course."""
        reg_clean = reg_no.strip().upper()
        code_clean = course_code.strip().upper()

        if reg_clean not in self._students:
            raise StudentNotFoundError(f"Student '{reg_clean}' not found.")
        if code_clean not in self._courses:
            raise CourseNotFoundError(f"Course '{code_clean}' not found.")

        student = self._students[reg_clean]
        if code_clean not in student.courses:
            student.enroll(code_clean)

        # Validate scores
        q = validate_score(quiz, ASSESSMENT_MAX_MARKS["quiz"], "Quiz") if quiz is not None else None
        a = validate_score(assignment, ASSESSMENT_MAX_MARKS["assignment"], "Assignment") if assignment is not None else None
        m = validate_score(midterm, ASSESSMENT_MAX_MARKS["midterm"], "Midterm") if midterm is not None else None
        f = validate_score(final, ASSESSMENT_MAX_MARKS["final"], "Final") if final is not None else None

        student.update_marks(code_clean, quiz=q, assignment=a, midterm=m, final=f)
        return student.courses[code_clean].marks

    def generate_student_transcript(self, reg_no: str) -> Dict[str, Any]:
        """Generate a complete academic grade card/transcript for a student."""
        reg_clean = reg_no.strip().upper()
        if reg_clean not in self._students:
            raise StudentNotFoundError(f"Student '{reg_clean}' not found.")

        student = self._students[reg_clean]
        records = []
        total_credits = 0
        earned_credits = 0

        for code, rec in student.courses.items():
            course = self._courses.get(code)
            c_title = course.title if course else "Unknown Course"
            c_credits = course.credits if course else 3

            total_credits += c_credits
            if rec.grade_point >= 5:
                earned_credits += c_credits

            records.append({
                "code": code,
                "title": c_title,
                "credits": c_credits,
                "quiz": rec.marks.get("quiz", 0.0),
                "assignment": rec.marks.get("assignment", 0.0),
                "midterm": rec.marks.get("midterm", 0.0),
                "final": rec.marks.get("final", 0.0),
                "total": rec.total_score,
                "attendance_pct": rec.attendance_percentage,
                "grade": rec.grade_letter,
                "grade_point": rec.grade_point,
                "status": rec.status,
            })

        gpa = student.calculate_gpa(self._courses)

        return {
            "reg_no": student.reg_no,
            "name": student.name,
            "branch": student.branch,
            "semester": student.semester,
            "total_credits": total_credits,
            "earned_credits": earned_credits,
            "gpa": gpa,
            "records": records,
        }

    def get_course_analytics(self, course_code: str) -> Dict[str, Any]:
        """Compute statistical analysis for a particular course."""
        code_clean = course_code.strip().upper()
        if code_clean not in self._courses:
            raise CourseNotFoundError(f"Course '{code_clean}' not found.")

        enrolled = [s for s in self._students.values() if code_clean in s.courses]
        if not enrolled:
            return {
                "course_code": code_clean,
                "enrolled_count": 0,
                "average_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "pass_percentage": 0.0,
                "grade_distribution": {},
            }

        scores = [s.courses[code_clean].total_score for s in enrolled]
        grade_dist = {letter: 0 for letter, _, _ in GRADE_SCALE}
        grade_dist["F (Debarred)"] = 0
        passes = 0

        for s in enrolled:
            rec = s.courses[code_clean]
            grade = rec.grade_letter
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
            if rec.status == "PASS":
                passes += 1

        avg_score = round(sum(scores) / len(scores), 2)
        pass_pct = round((passes / len(enrolled)) * 100.0, 2)

        return {
            "course_code": code_clean,
            "course_title": self._courses[code_clean].title,
            "enrolled_count": len(enrolled),
            "average_score": avg_score,
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "pass_percentage": pass_pct,
            "grade_distribution": grade_dist,
        }

    def get_leaderboard(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Return the top N students ranked by GPA."""
        ranked = []
        for s in self._students.values():
            gpa = s.calculate_gpa(self._courses)
            ranked.append({
                "reg_no": s.reg_no,
                "name": s.name,
                "branch": s.branch,
                "gpa": gpa,
                "courses_enrolled": len(s.courses),
            })

        ranked.sort(key=lambda item: item["gpa"], reverse=True)
        return ranked[:top_n]
