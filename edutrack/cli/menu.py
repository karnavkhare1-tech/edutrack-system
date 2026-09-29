"""Command Line Interface (CLI) menu system for EduTrack.

Provides an interactive console interface for student management,
course enrollments, attendance audits, academic grading, and report exports.
"""

import sys
from typing import Dict, List
from ..models import Student, Course, Faculty
from ..services import StudentService, CourseService, AttendanceService, AnalyticsService
from ..storage import DataStorage
from ..utils.exceptions import EduTrackException
from ..data_seed import generate_seed_data
from ..config import MIN_ATTENDANCE_PERCENTAGE


class Colors:
    """ANSI color escape sequences for modern CLI aesthetic."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def styled(text: str, color_code: str) -> str:
    """Format string with color code."""
    return f"{color_code}{text}{Colors.END}"


class EduTrackCLI:
    """Main CLI Application Controller."""

    def __init__(self, storage: DataStorage):
        self.storage = storage
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}
        self.faculty: Dict[str, Faculty] = {}

        self._load_or_initialize()

        # Initialize Services
        self.student_service = StudentService(self.students)
        self.course_service = CourseService(self.courses, self.students)
        self.attendance_service = AttendanceService(self.students)
        self.analytics_service = AnalyticsService(self.students, self.courses)

    def _load_or_initialize(self):
        """Load data from JSON storage; populate seed data if empty."""
        raw = self.storage.load_data()
        raw_students = raw.get("students", {})
        raw_courses = raw.get("courses", {})
        raw_faculty = raw.get("faculty", {})

        if not raw_students and not raw_courses:
            print(styled("\n[Info] No existing database found. Generating default seed dataset...", Colors.YELLOW))
            f_seed, c_seed, s_seed = generate_seed_data()
            self.faculty = f_seed
            self.courses = c_seed
            self.students = s_seed
            self.save()
            print(styled("[Success] Sample database seeded with students, courses, and attendance records.", Colors.GREEN))
        else:
            self.students = {reg: Student.from_dict(d) for reg, d in raw_students.items()}
            self.courses = {code: Course.from_dict(d) for code, d in raw_courses.items()}
            self.faculty = {eid: Faculty.from_dict(d) for eid, d in raw_faculty.items()}

    def save(self):
        """Persist state to storage."""
        self.storage.save_data(self.students, self.courses, self.faculty)

    # -------------------------------------------------------------
    # MAIN MENU
    # -------------------------------------------------------------
    def start(self):
        """Main application interactive loop."""
        while True:
            self._print_header()
            print(f"{Colors.BOLD}1.{Colors.END} Student Management (Add, View, Update, Delete)")
            print(f"{Colors.BOLD}2.{Colors.END} Course Catalog & Enrollments")
            print(f"{Colors.BOLD}3.{Colors.END} Attendance Tracking & 75% Rule Compliance")
            print(f"{Colors.BOLD}4.{Colors.END} Academic Marks, GPA & Performance Analytics")
            print(f"{Colors.BOLD}5.{Colors.END} Export Reports & Data Management (CSV Export)")
            print(f"{Colors.BOLD}0.{Colors.END} Save & Exit")
            print("-" * 65)

            choice = input(styled("Select an option [0-5]: ", Colors.BOLD)).strip()

            if choice == "1":
                self._menu_students()
            elif choice == "2":
                self._menu_courses()
            elif choice == "3":
                self._menu_attendance()
            elif choice == "4":
                self._menu_analytics()
            elif choice == "5":
                self._menu_reports()
            elif choice == "0":
                self.save()
                print(styled("\nData saved successfully. Thank you for using EduTrack!", Colors.GREEN))
                break
            else:
                print(styled("Invalid option. Please choose between 0 and 5.", Colors.RED))
                input("Press [Enter] to continue...")

    def _print_header(self):
        print("\n" + "=" * 65)
        print(styled("       EDUTRACK - ACADEMIC & ATTENDANCE MANAGEMENT SYSTEM", Colors.CYAN + Colors.BOLD))
        print(styled("        Empowering Student Success & Institutional Insights", Colors.YELLOW))
        print("=" * 65)
        print(f" Registered Students: {len(self.students)} | Active Courses: {len(self.courses)}")
        print("=" * 65)

    # -------------------------------------------------------------
    # MODULE 1: STUDENT MANAGEMENT
    # -------------------------------------------------------------
    def _menu_students(self):
        while True:
            print("\n" + "-" * 55)
            print(styled(">>> MODULE 1: STUDENT MANAGEMENT", Colors.CYAN + Colors.BOLD))
            print("-" * 55)
            print("1. Register New Student")
            print("2. View Student Profile & Enrolled Courses")
            print("3. List All Students")
            print("4. Search Students (by Reg No or Name)")
            print("5. Update Student Information")
            print("6. Delete Student Record")
            print("0. Back to Main Menu")

            choice = input("\nEnter choice [0-6]: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._action_add_student()
            elif choice == "2":
                self._action_view_student()
            elif choice == "3":
                self._action_list_students()
            elif choice == "4":
                self._action_search_students()
            elif choice == "5":
                self._action_update_student()
            elif choice == "6":
                self._action_delete_student()
            else:
                print(styled("Invalid choice.", Colors.RED))

    def _action_add_student(self):
        print("\n--- Register New Student ---")
        reg_no = input("Registration Number (e.g. 24BCE1006): ")
        name = input("Student Full Name: ")
        email = input("Email Address: ")
        branch = input("Branch/Specialization (e.g. BCE, BME): ")
        semester = input("Current Semester (default 1): ").strip() or "1"
        phone = input("Phone Number (optional): ")

        try:
            student = self.student_service.add_student(
                reg_no=reg_no,
                name=name,
                email=email,
                branch=branch,
                semester=int(semester),
                phone=phone,
            )
            self.save()
            print(styled(f"\n[Success] Student '{student.name}' ({student.reg_no}) registered successfully!", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"\n[Error] {e.message}", Colors.RED))
        except Exception as e:
            print(styled(f"\n[Error] Failed to add student: {e}", Colors.RED))

    def _action_view_student(self):
        reg = input("\nEnter Student Registration Number: ").strip()
        try:
            s = self.student_service.get_student(reg)
            print("\n" + "=" * 50)
            print(styled(f"STUDENT PROFILE: {s.name}", Colors.BOLD))
            print("=" * 50)
            print(f"Reg No   : {s.reg_no}")
            print(f"Email    : {s.email}")
            print(f"Branch   : {s.branch}")
            print(f"Semester : {s.semester}")
            print(f"Phone    : {s.phone if s.phone else 'N/A'}")
            print(f"Enrolled : {', '.join(s.courses.keys()) if s.courses else 'None'}")
            print(f"GPA      : {s.calculate_gpa(self.courses):.2f}")
            print("=" * 50)
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_list_students(self):
        students = self.student_service.list_all()
        if not students:
            print(styled("\nNo students registered yet.", Colors.YELLOW))
            return

        print("\n" + "=" * 80)
        print(f"{'Reg No':<14} | {'Name':<22} | {'Branch':<8} | {'Sem':<5} | {'Courses':<8} | {'GPA':<5}")
        print("=" * 80)
        for s in students:
            gpa = s.calculate_gpa(self.courses)
            print(f"{s.reg_no:<14} | {s.name:<22} | {s.branch:<8} | {s.semester:<5} | {len(s.courses):<8} | {gpa:<5.2f}")
        print("=" * 80)

    def _action_search_students(self):
        q = input("\nEnter search query (Registration Number or Name): ").strip()
        results = self.student_service.search(q)
        if not results:
            print(styled(f"No students matching '{q}' found.", Colors.YELLOW))
            return

        print(styled(f"\nFound {len(results)} matching student(s):", Colors.GREEN))
        for s in results:
            print(f"- [{s.reg_no}] {s.name} ({s.branch}, Sem {s.semester}) - {s.email}")

    def _action_update_student(self):
        reg = input("\nEnter Student Registration Number to update: ").strip()
        try:
            s = self.student_service.get_student(reg)
            print(f"Updating profile for: {s.name} ({s.reg_no})")
            print("(Leave blank to keep existing value)")
            name = input(f"New Name [{s.name}]: ").strip() or None
            email = input(f"New Email [{s.email}]: ").strip() or None
            branch = input(f"New Branch [{s.branch}]: ").strip() or None
            sem_in = input(f"New Semester [{s.semester}]: ").strip()
            semester = int(sem_in) if sem_in else None
            phone = input(f"New Phone [{s.phone}]: ").strip() or None

            self.student_service.update_student(
                reg_no=reg,
                name=name,
                email=email,
                branch=branch,
                semester=semester,
                phone=phone,
            )
            self.save()
            print(styled(f"\n[Success] Student '{reg}' profile updated.", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_delete_student(self):
        reg = input("\nEnter Registration Number to delete: ").strip()
        confirm = input(styled(f"Are you sure you want to permanently delete {reg}? (yes/no): ", Colors.YELLOW)).strip().lower()
        if confirm == "yes":
            try:
                self.student_service.delete_student(reg)
                self.save()
                print(styled(f"[Success] Student '{reg}' removed.", Colors.GREEN))
            except EduTrackException as e:
                print(styled(f"[Error] {e.message}", Colors.RED))
        else:
            print("Deletion cancelled.")

    # -------------------------------------------------------------
    # MODULE 2: COURSE CATALOG & ENROLLMENTS
    # -------------------------------------------------------------
    def _menu_courses(self):
        while True:
            print("\n" + "-" * 55)
            print(styled(">>> MODULE 2: COURSE CATALOG & ENROLLMENTS", Colors.CYAN + Colors.BOLD))
            print("-" * 55)
            print("1. Add New Course Offering")
            print("2. View Course Catalog")
            print("3. Enroll Student in Course")
            print("4. Drop Course for Student")
            print("5. View Enrolled Students for a Course")
            print("0. Back to Main Menu")

            choice = input("\nEnter choice [0-5]: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._action_add_course()
            elif choice == "2":
                self._action_list_courses()
            elif choice == "3":
                self._action_enroll_student()
            elif choice == "4":
                self._action_drop_course()
            elif choice == "5":
                self._action_view_enrolled()
            else:
                print(styled("Invalid choice.", Colors.RED))

    def _action_add_course(self):
        print("\n--- Add Course Offering ---")
        code = input("Course Code (e.g. CSE1002): ")
        title = input("Course Title: ")
        credits_in = input("Credits (1-5, default 3): ").strip() or "3"
        faculty = input("Faculty Instructor Name: ").strip() or "TBA"
        slot = input("Time Slot (e.g. A1, B2): ").strip() or "A1"
        capacity = input("Seat Capacity (default 60): ").strip() or "60"

        try:
            c = self.course_service.add_course(
                code=code,
                title=title,
                credits=int(credits_in),
                faculty_name=faculty,
                slot=slot,
                max_capacity=int(capacity),
            )
            self.save()
            print(styled(f"\n[Success] Course '{c.code} - {c.title}' added to catalog!", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_list_courses(self):
        courses = self.course_service.list_all()
        if not courses:
            print(styled("\nNo courses in catalog.", Colors.YELLOW))
            return

        print("\n" + "=" * 90)
        print(f"{'Code':<10} | {'Title':<35} | {'Credits':<8} | {'Slot':<8} | {'Enrolled':<10} | {'Faculty':<15}")
        print("=" * 90)
        for c in courses:
            enrolled = len(self.course_service.get_enrolled_students(c.code))
            print(f"{c.code:<10} | {c.title[:35]:<35} | {c.credits:<8} | {c.slot:<8} | {enrolled}/{c.max_capacity:<8} | {c.faculty_name[:15]:<15}")
        print("=" * 90)

    def _action_enroll_student(self):
        reg = input("\nStudent Registration Number: ").strip()
        code = input("Course Code: ").strip()
        try:
            self.course_service.enroll_student(reg, code)
            self.save()
            print(styled(f"[Success] Student '{reg}' successfully enrolled in '{code}'!", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_drop_course(self):
        reg = input("\nStudent Registration Number: ").strip()
        code = input("Course Code: ").strip()
        try:
            if self.course_service.drop_student(reg, code):
                self.save()
                print(styled(f"[Success] Dropped '{code}' for student '{reg}'.", Colors.GREEN))
            else:
                print(styled(f"Student was not enrolled in '{code}'.", Colors.YELLOW))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_view_enrolled(self):
        code = input("\nEnter Course Code: ").strip()
        try:
            c = self.course_service.get_course(code)
            enrolled = self.course_service.get_enrolled_students(code)
            print(f"\nCourse: {c.code} - {c.title} (Faculty: {c.faculty_name})")
            print(f"Total Enrolled: {len(enrolled)} / {c.max_capacity}")
            if not enrolled:
                print("No students enrolled yet.")
                return

            print("-" * 55)
            for s in enrolled:
                rec = s.courses[c.code]
                print(f"- [{s.reg_no}] {s.name:<22} | Att: {rec.attendance_percentage}% | Score: {rec.total_score}")
            print("-" * 55)
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    # -------------------------------------------------------------
    # MODULE 3: ATTENDANCE TRACKING & 75% RULE COMPLIANCE
    # -------------------------------------------------------------
    def _menu_attendance(self):
        while True:
            print("\n" + "-" * 55)
            print(styled(">>> MODULE 3: ATTENDANCE & 75% ELIGIBILITY", Colors.CYAN + Colors.BOLD))
            print("-" * 55)
            print("1. Update Cumulative Attendance for Student")
            print("2. Conduct Class Session (Mark Present/Absent)")
            print("3. View Student Attendance Status & Margin Advice")
            print(f"4. View Debarred Students List (< {MIN_ATTENDANCE_PERCENTAGE}%)")
            print("0. Back to Main Menu")

            choice = input("\nEnter choice [0-4]: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._action_update_attendance()
            elif choice == "2":
                self._action_conduct_session()
            elif choice == "3":
                self._action_attendance_status()
            elif choice == "4":
                self._action_list_debarred()
            else:
                print(styled("Invalid choice.", Colors.RED))

    def _action_update_attendance(self):
        reg = input("\nStudent Registration Number: ").strip()
        code = input("Course Code: ").strip()
        try:
            att = int(input("Attended Classes count: "))
            tot = int(input("Total Conducted Classes count: "))
            rec = self.attendance_service.log_student_attendance(reg, code, att, tot)
            self.save()
            print(styled(f"\n[Success] Attendance updated for {reg} in {code}: {rec.attended_classes}/{rec.total_classes} ({rec.attendance_percentage}%)", Colors.GREEN))
            print(f"Advice: {rec.attendance_advice()}")
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))
        except ValueError:
            print(styled("[Error] Please enter valid integers.", Colors.RED))

    def _action_conduct_session(self):
        code = input("\nEnter Course Code for today's session: ").strip()
        try:
            self.course_service.get_course(code)
            enrolled = self.course_service.get_enrolled_students(code)
            if not enrolled:
                print(styled(f"No students enrolled in {code}.", Colors.YELLOW))
                return

            print(f"\nConducting Attendance Session for {code}. Total enrolled: {len(enrolled)}")
            print("Enter 'p' for Present, 'a' for Absent (Default is Present):")
            present_list = []
            for s in enrolled:
                resp = input(f"Student [{s.reg_no}] {s.name}: ").strip().lower()
                if resp != "a":
                    present_list.append(s.reg_no)

            self.attendance_service.record_session(code, present_list)
            self.save()
            print(styled(f"\n[Success] Session attendance recorded! Present: {len(present_list)}, Absent: {len(enrolled) - len(present_list)}", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_attendance_status(self):
        reg = input("\nStudent Registration Number: ").strip()
        try:
            summary = self.attendance_service.get_student_summary(reg)
            if not summary:
                print(styled(f"Student {reg} is not enrolled in any courses.", Colors.YELLOW))
                return

            print("\n" + "=" * 80)
            print(styled(f"ATTENDANCE AUDIT FOR STUDENT: {reg}", Colors.BOLD))
            print("=" * 80)
            for row in summary:
                status_str = styled("ELIGIBLE", Colors.GREEN) if not row["is_debarred"] else styled("DEBARRED (<75%)", Colors.RED + Colors.BOLD)
                print(f"Course: {row['course_code']} | Attended: {row['attended']}/{row['total']} ({row['percentage']}%) | Status: {status_str}")
                print(f"  Advice: {row['advice']}")
                print("-" * 80)
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_list_debarred(self):
        code = input("\nEnter Course Code to filter (or press Enter for all courses): ").strip()
        debarred = self.attendance_service.get_debarred_students(code)
        if not debarred:
            print(styled(f"\nGreat news! No students are currently debarred (< {MIN_ATTENDANCE_PERCENTAGE}% attendance).", Colors.GREEN))
            return

        print("\n" + "=" * 80)
        print(styled(f"CRITICAL: DEBARRED STUDENTS LIST (< {MIN_ATTENDANCE_PERCENTAGE}% ATTENDANCE)", Colors.RED + Colors.BOLD))
        print("=" * 80)
        print(f"{'Reg No':<14} | {'Name':<22} | {'Course':<10} | {'Attendance':<15} | {'Recovery Required'}")
        print("=" * 80)
        for s, c_code, rec in debarred:
            needed = (3 * rec.total_classes) - (4 * rec.attended_classes)
            print(f"{s.reg_no:<14} | {s.name:<22} | {c_code:<10} | {rec.attended_classes}/{rec.total_classes} ({rec.attendance_percentage}%) | Must attend next {max(0, needed)} classes")
        print("=" * 80)

    # -------------------------------------------------------------
    # MODULE 4: ACADEMIC MARKS, GPA & ANALYTICS
    # -------------------------------------------------------------
    def _menu_analytics(self):
        while True:
            print("\n" + "-" * 55)
            print(styled(">>> MODULE 4: MARKS, GPA & ANALYTICS", Colors.CYAN + Colors.BOLD))
            print("-" * 55)
            print("1. Enter / Update Student Assessment Marks")
            print("2. View Student Academic Transcript & GPA")
            print("3. View Course Statistical Analytics & Grade Distribution")
            print("4. View Top Rankers Leaderboard (Dean's Honor Roll)")
            print("0. Back to Main Menu")

            choice = input("\nEnter choice [0-4]: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                self._action_enter_marks()
            elif choice == "2":
                self._action_student_transcript()
            elif choice == "3":
                self._action_course_analytics()
            elif choice == "4":
                self._action_leaderboard()
            else:
                print(styled("Invalid choice.", Colors.RED))

    def _action_enter_marks(self):
        reg = input("\nStudent Registration Number: ").strip()
        code = input("Course Code: ").strip()
        try:
            print("Enter marks (Leave blank to keep current score):")
            q_in = input("Quiz (Max 10): ").strip()
            a_in = input("Assignment (Max 20): ").strip()
            m_in = input("Midterm Exam (Max 30): ").strip()
            f_in = input("Final Exam (Max 40): ").strip()

            q = float(q_in) if q_in else None
            a = float(a_in) if a_in else None
            m = float(m_in) if m_in else None
            f = float(f_in) if f_in else None

            self.analytics_service.record_student_marks(reg, code, quiz=q, assignment=a, midterm=m, final=f)
            self.save()
            print(styled(f"[Success] Marks updated for {reg} in {code}!", Colors.GREEN))
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))
        except ValueError:
            print(styled("[Error] Invalid numerical score entered.", Colors.RED))

    def _action_student_transcript(self):
        reg = input("\nStudent Registration Number: ").strip()
        try:
            transcript = self.analytics_service.generate_student_transcript(reg)
            print("\n" + "=" * 90)
            print(styled(f"ACADEMIC TRANSCRIPT: {transcript['name']} ({transcript['reg_no']})", Colors.BOLD))
            print(f"Branch: {transcript['branch']} | Semester: {transcript['semester']} | Total Credits: {transcript['total_credits']}")
            print("=" * 90)
            print(f"{'Course':<10} | {'Title':<25} | {'Cr':<3} | {'Quiz':<5} | {'Asgn':<5} | {'Mid':<5} | {'Fin':<5} | {'Tot':<5} | {'Att%':<6} | {'Grd':<4} | {'Status'}")
            print("-" * 90)
            for r in transcript["records"]:
                print(f"{r['code']:<10} | {r['title'][:25]:<25} | {r['credits']:<3} | {r['quiz']:<5.1f} | {r['assignment']:<5.1f} | {r['midterm']:<5.1f} | {r['final']:<5.1f} | {r['total']:<5.1f} | {r['attendance_pct']:<6.1f} | {r['grade']:<4} | {r['status']}")
            print("=" * 90)
            print(styled(f"SEMESTER GRADE POINT AVERAGE (SGPA): {transcript['gpa']:.2f} / 10.00", Colors.CYAN + Colors.BOLD))
            print("=" * 90)
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_course_analytics(self):
        code = input("\nEnter Course Code: ").strip()
        try:
            stats = self.analytics_service.get_course_analytics(code)
            if stats["enrolled_count"] == 0:
                print(styled(f"No students enrolled in {code}.", Colors.YELLOW))
                return

            print("\n" + "=" * 60)
            print(styled(f"ANALYTICS REPORT: {stats['course_code']} - {stats['course_title']}", Colors.BOLD))
            print("=" * 60)
            print(f"Enrolled Students : {stats['enrolled_count']}")
            print(f"Average Score     : {stats['average_score']} / 100")
            print(f"Highest Score     : {stats['highest_score']} / 100")
            print(f"Lowest Score      : {stats['lowest_score']} / 100")
            print(f"Passing Rate      : {stats['pass_percentage']}%")
            print("-" * 60)
            print("Grade Distribution Breakdown:")
            for grade, count in stats["grade_distribution"].items():
                bar = "█" * count
                print(f"  Grade {grade:<12}: {count:<3} {bar}")
            print("=" * 60)
        except EduTrackException as e:
            print(styled(f"[Error] {e.message}", Colors.RED))

    def _action_leaderboard(self):
        top = self.analytics_service.get_leaderboard(top_n=5)
        print("\n" + "=" * 65)
        print(styled("TOP PERFORMERS LEADERBOARD (DEAN'S HONOR ROLL)", Colors.YELLOW + Colors.BOLD))
        print("=" * 65)
        print(f"{'Rank':<5} | {'Reg No':<14} | {'Name':<22} | {'Branch':<8} | {'GPA':<5}")
        print("-" * 65)
        for idx, item in enumerate(top, 1):
            rank_str = f"#{idx}"
            if idx == 1:
                rank_str = styled("🥇 #1", Colors.YELLOW)
            elif idx == 2:
                rank_str = styled("🥈 #2", Colors.CYAN)
            elif idx == 3:
                rank_str = styled("🥉 #3", Colors.GREEN)
            print(f"{rank_str:<14} | {item['reg_no']:<14} | {item['name']:<22} | {item['branch']:<8} | {item['gpa']:<5.2f}")
        print("=" * 65)

    # -------------------------------------------------------------
    # MODULE 5: CSV REPORTS & DATA MANAGEMENT
    # -------------------------------------------------------------
    def _menu_reports(self):
        while True:
            print("\n" + "-" * 55)
            print(styled(">>> MODULE 5: CSV REPORTS & DATA MANAGEMENT", Colors.CYAN + Colors.BOLD))
            print("-" * 55)
            print("1. Export Students Academic Summary to CSV")
            print("2. Export Complete Attendance Audit to CSV")
            print("3. Reset Database to Default Seed Data")
            print("0. Back to Main Menu")

            choice = input("\nEnter choice [0-3]: ").strip()
            if choice == "0":
                break
            elif choice == "1":
                path = self.storage.export_students_csv(list(self.students.values()), self.courses)
                print(styled(f"[Success] Student summary exported to:\n  {path.resolve()}", Colors.GREEN))
            elif choice == "2":
                path = self.storage.export_attendance_csv(list(self.students.values()))
                print(styled(f"[Success] Attendance report exported to:\n  {path.resolve()}", Colors.GREEN))
            elif choice == "3":
                confirm = input(styled("Are you sure you want to reset all data to default? (yes/no): ", Colors.RED)).strip().lower()
                if confirm == "yes":
                    f_seed, c_seed, s_seed = generate_seed_data()
                    self.faculty = f_seed
                    self.courses = c_seed
                    self.students = s_seed
                    self.student_service = StudentService(self.students)
                    self.course_service = CourseService(self.courses, self.students)
                    self.attendance_service = AttendanceService(self.students)
                    self.analytics_service = AnalyticsService(self.students, self.courses)
                    self.save()
                    print(styled("[Success] System reset to default sample dataset.", Colors.GREEN))
            else:
                print(styled("Invalid choice.", Colors.RED))
