"""EduTrack Web Application Server.

Lightweight, zero-dependency HTTP server utilizing Python standard library
(http.server, socketserver, json) providing REST API endpoints and serving
the modern responsive web interface.
"""

import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
import webbrowser
import threading

from ..models import Student, Course, Faculty
from ..services import StudentService, CourseService, AttendanceService, AnalyticsService
from ..storage import DataStorage
from ..utils.exceptions import EduTrackException
from ..data_seed import generate_seed_data
from .. import __version__

WEB_DIR = Path(__file__).resolve().parent


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP server to process requests concurrently."""
    daemon_threads = True


class EduTrackApiHandler(BaseHTTPRequestHandler):
    """Custom request handler with REST API routing and static file serving."""

    # Server-wide references set by launcher
    storage: DataStorage = None
    students = {}
    courses = {}
    faculty = {}
    student_svc: StudentService = None
    course_svc: CourseService = None
    attendance_svc: AttendanceService = None
    analytics_svc: AnalyticsService = None
    lock = threading.Lock()

    def log_message(self, format, *args):
        """Suppress noisy request logging in terminal, keep errors."""
        if args and str(args[1]) in ("400", "404", "500"):
            super().log_message(format, *args)

    def _send_json(self, status_code: int, data: dict):
        """Helper to send JSON response."""
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def _send_error(self, status_code: int, message: str):
        """Helper to send structured error response."""
        self._send_json(status_code, {"success": False, "error": message})

    def _read_json_body(self) -> dict:
        """Parse request body as JSON."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # -------------------------------------------------------------
    # GET ROUTES
    # -------------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # Static assets
        if path == "/":
            return self._serve_file(WEB_DIR / "index.html", "text/html")
        elif path == "/style.css":
            return self._serve_file(WEB_DIR / "style.css", "text/css")
        elif path == "/app.js":
            return self._serve_file(WEB_DIR / "app.js", "application/javascript")

        # API Endpoints
        if path == "/api/overview":
            return self._handle_get_overview()
        elif path == "/api/students":
            return self._handle_get_students()
        elif path == "/api/courses":
            return self._handle_get_courses()
        elif path.startswith("/api/transcript/"):
            reg_no = path.split("/")[-1]
            return self._handle_get_transcript(reg_no)
        elif path.startswith("/api/audit/"):
            reg_no = path.split("/")[-1]
            return self._handle_get_audit(reg_no)
        elif path.startswith("/api/course-analytics/"):
            code = path.split("/")[-1]
            return self._handle_get_course_analytics(code)

        self._send_error(404, f"Endpoint '{path}' not found")

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self._send_error(404, f"File {file_path.name} not found")
            return
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def _handle_get_overview(self):
        with self.lock:
            students_list = []
            total_gpa = 0.0
            gpa_count = 0
            debarred_enrollments = 0

            for s in self.students.values():
                gpa = s.calculate_gpa(self.courses)
                if len(s.courses) > 0:
                    total_gpa += gpa
                    gpa_count += 1

                for rec in s.courses.values():
                    if rec.is_attendance_debarred:
                        debarred_enrollments += 1

                students_list.append({
                    "reg_no": s.reg_no,
                    "name": s.name,
                    "email": s.email,
                    "branch": s.branch,
                    "semester": s.semester,
                    "phone": s.phone,
                    "gpa": gpa,
                    "courses_count": len(s.courses),
                })

            avg_gpa = round(total_gpa / gpa_count, 2) if gpa_count > 0 else 0.0
            leaderboard = self.analytics_svc.get_leaderboard(top_n=5)
            debarred_raw = self.attendance_svc.get_debarred_students()
            debarred_list = []
            for st, code, rec in debarred_raw:
                debarred_list.append({
                    "reg_no": st.reg_no,
                    "name": st.name,
                    "course_code": code,
                    "attended": rec.attended_classes,
                    "total": rec.total_classes,
                    "percentage": rec.attendance_percentage,
                    "advice": rec.attendance_advice(),
                })

            courses_list = []
            for c in self.courses.values():
                enrolled_students = self.course_svc.get_enrolled_students(c.code)
                courses_list.append({
                    "code": c.code,
                    "title": c.title,
                    "credits": c.credits,
                    "faculty_name": c.faculty_name,
                    "slot": c.slot,
                    "max_capacity": c.max_capacity,
                    "enrolled_count": len(enrolled_students),
                })

            data = {
                "success": True,
                "version": __version__,
                "stats": {
                    "total_students": len(self.students),
                    "total_courses": len(self.courses),
                    "total_faculty": len(self.faculty),
                    "average_gpa": avg_gpa,
                    "debarred_count": len(debarred_list),
                },
                "leaderboard": leaderboard,
                "debarred": debarred_list,
                "students": students_list,
                "courses": courses_list,
            }
            self._send_json(200, data)

    def _handle_get_students(self):
        with self.lock:
            result = []
            for s in self.student_svc.list_all():
                gpa = s.calculate_gpa(self.courses)
                courses_info = []
                for c_code, rec in s.courses.items():
                    c_obj = self.courses.get(c_code)
                    courses_info.append({
                        "code": c_code,
                        "title": c_obj.title if c_obj else c_code,
                        "credits": c_obj.credits if c_obj else 3,
                        "attended": rec.attended_classes,
                        "total": rec.total_classes,
                        "percentage": rec.attendance_percentage,
                        "is_debarred": rec.is_attendance_debarred,
                        "grade": rec.grade_letter,
                        "status": rec.status,
                        "total_score": rec.total_score,
                    })
                result.append({
                    "reg_no": s.reg_no,
                    "name": s.name,
                    "email": s.email,
                    "branch": s.branch,
                    "semester": s.semester,
                    "phone": s.phone,
                    "gpa": gpa,
                    "courses": courses_info,
                })
            self._send_json(200, {"success": True, "students": result})

    def _handle_get_courses(self):
        with self.lock:
            result = []
            for c in self.course_svc.list_all():
                enrolled = self.course_svc.get_enrolled_students(c.code)
                result.append({
                    "code": c.code,
                    "title": c.title,
                    "credits": c.credits,
                    "faculty_name": c.faculty_name,
                    "slot": c.slot,
                    "max_capacity": c.max_capacity,
                    "enrolled_count": len(enrolled),
                    "enrolled_reg_nos": [s.reg_no for s in enrolled],
                })
            self._send_json(200, {"success": True, "courses": result})

    def _handle_get_transcript(self, reg_no: str):
        with self.lock:
            try:
                transcript = self.analytics_svc.generate_student_transcript(reg_no)
                self._send_json(200, {"success": True, "transcript": transcript})
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_get_audit(self, reg_no: str):
        with self.lock:
            try:
                summary = self.attendance_svc.get_student_summary(reg_no)
                self._send_json(200, {"success": True, "audit": summary})
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_get_course_analytics(self, course_code: str):
        with self.lock:
            try:
                analytics = self.analytics_svc.get_course_analytics(course_code)
                self._send_json(200, {"success": True, "analytics": analytics})
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    # -------------------------------------------------------------
    # POST / PUT / DELETE ROUTES
    # -------------------------------------------------------------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._read_json_body()

        with self.lock:
            try:
                if path == "/api/students":
                    return self._action_add_student(data)
                elif path == "/api/courses":
                    return self._action_add_course(data)
                elif path == "/api/enroll":
                    return self._action_enroll(data)
                elif path == "/api/drop":
                    return self._action_drop(data)
                elif path == "/api/attendance":
                    return self._action_attendance(data)
                elif path == "/api/attendance/session":
                    return self._action_attendance_session(data)
                elif path == "/api/marks":
                    return self._action_marks(data)
                elif path == "/api/export":
                    return self._action_export()
                elif path == "/api/reset":
                    return self._action_reset()
                else:
                    self._send_error(404, f"POST endpoint '{path}' not found")
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = self._read_json_body()

        with self.lock:
            try:
                if path.startswith("/api/students/"):
                    reg_no = path.split("/")[-1]
                    updated = self.student_svc.update_student(
                        reg_no=reg_no,
                        name=data.get("name"),
                        email=data.get("email"),
                        branch=data.get("branch"),
                        semester=data.get("semester"),
                        phone=data.get("phone"),
                    )
                    self._save_state()
                    self._send_json(200, {"success": True, "student": updated.to_dict()})
                elif path.startswith("/api/courses/"):
                    code = path.split("/")[-1]
                    updated = self.course_svc.update_course(
                        code=code,
                        title=data.get("title"),
                        credits=data.get("credits"),
                        faculty_name=data.get("faculty_name"),
                        slot=data.get("slot"),
                    )
                    self._save_state()
                    self._send_json(200, {"success": True, "course": updated.to_dict()})
                else:
                    self._send_error(404, f"PUT endpoint '{path}' not found")
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        with self.lock:
            try:
                if path.startswith("/api/students/"):
                    reg_no = path.split("/")[-1]
                    self.student_svc.delete_student(reg_no)
                    self._save_state()
                    self._send_json(200, {"success": True, "message": f"Student '{reg_no}' deleted"})
                elif path.startswith("/api/courses/"):
                    code = path.split("/")[-1]
                    self.course_svc.delete_course(code)
                    self._save_state()
                    self._send_json(200, {"success": True, "message": f"Course '{code}' deleted"})
                else:
                    self._send_error(404, f"DELETE endpoint '{path}' not found")
            except EduTrackException as e:
                self._send_error(400, e.message)
            except Exception as e:
                self._send_error(500, str(e))

    # --- Actions ---
    def _action_add_student(self, data: dict):
        reg_no = data.get("reg_no", "")
        name = data.get("name", "")
        email = data.get("email", "")
        branch = data.get("branch", "")
        semester = int(data.get("semester", 1))
        phone = data.get("phone", "")

        student = self.student_svc.add_student(
            reg_no=reg_no,
            name=name,
            email=email,
            branch=branch,
            semester=semester,
            phone=phone,
        )
        self._save_state()
        self._send_json(201, {"success": True, "student": student.to_dict()})

    def _action_add_course(self, data: dict):
        code = data.get("code", "")
        title = data.get("title", "")
        credits = int(data.get("credits", 4))
        faculty_name = data.get("faculty_name", "TBA")
        slot = data.get("slot", "A1")
        max_capacity = int(data.get("max_capacity", 60))

        course = self.course_svc.add_course(
            code=code,
            title=title,
            credits=credits,
            faculty_name=faculty_name,
            slot=slot,
            max_capacity=max_capacity,
        )
        self._save_state()
        self._send_json(201, {"success": True, "course": course.to_dict()})

    def _action_enroll(self, data: dict):
        reg_no = data.get("reg_no", "")
        course_code = data.get("course_code", "")
        self.course_svc.enroll_student(reg_no, course_code)
        self._save_state()
        self._send_json(200, {"success": True, "message": f"Enrolled {reg_no} into {course_code}"})

    def _action_drop(self, data: dict):
        reg_no = data.get("reg_no", "")
        course_code = data.get("course_code", "")
        self.course_svc.drop_student(reg_no, course_code)
        self._save_state()
        self._send_json(200, {"success": True, "message": f"Dropped {reg_no} from {course_code}"})

    def _action_attendance(self, data: dict):
        reg_no = data.get("reg_no", "")
        course_code = data.get("course_code", "")
        attended = int(data.get("attended", 0))
        total = int(data.get("total", 0))

        rec = self.attendance_svc.log_student_attendance(reg_no, course_code, attended, total)
        self._save_state()
        self._send_json(200, {
            "success": True,
            "record": {
                "attended": rec.attended_classes,
                "total": rec.total_classes,
                "percentage": rec.attendance_percentage,
                "is_debarred": rec.is_attendance_debarred,
                "advice": rec.attendance_advice(),
            }
        })

    def _action_attendance_session(self, data: dict):
        course_code = data.get("course_code", "")
        present_reg_nos = data.get("present_reg_nos", [])
        results = self.attendance_svc.record_session(course_code, present_reg_nos)
        self._save_state()
        self._send_json(200, {"success": True, "results": results})

    def _action_marks(self, data: dict):
        reg_no = data.get("reg_no", "")
        course_code = data.get("course_code", "")
        quiz = float(data["quiz"]) if "quiz" in data and data["quiz"] is not None and str(data["quiz"]).strip() != "" else None
        assignment = float(data["assignment"]) if "assignment" in data and data["assignment"] is not None and str(data["assignment"]).strip() != "" else None
        midterm = float(data["midterm"]) if "midterm" in data and data["midterm"] is not None and str(data["midterm"]).strip() != "" else None
        final = float(data["final"]) if "final" in data and data["final"] is not None and str(data["final"]).strip() != "" else None

        marks = self.analytics_svc.record_student_marks(
            reg_no, course_code, quiz=quiz, assignment=assignment, midterm=midterm, final=final
        )
        self._save_state()
        student = self.students[reg_no.strip().upper()]
        rec = student.courses[course_code.strip().upper()]
        self._send_json(200, {
            "success": True,
            "marks": marks,
            "total_score": rec.total_score,
            "grade": rec.grade_letter,
            "grade_point": rec.grade_point,
            "status": rec.status,
            "student_gpa": student.calculate_gpa(self.courses),
        })

    def _action_export(self):
        csv_students = self.storage.export_students_csv(list(self.students.values()), self.courses)
        csv_attendance = self.storage.export_attendance_csv(list(self.students.values()))
        self._send_json(200, {
            "success": True,
            "message": "CSV reports generated successfully in reports/ directory.",
            "files": [csv_students.name, csv_attendance.name],
        })

    def _action_reset(self):
        f_seed, c_seed, s_seed = generate_seed_data()
        self.faculty.clear()
        self.faculty.update(f_seed)
        self.courses.clear()
        self.courses.update(c_seed)
        self.students.clear()
        self.students.update(s_seed)
        self._save_state()
        self._send_json(200, {"success": True, "message": "Database reset to seed data"})

    def _save_state(self):
        """Helper to sync in-memory dicts with JSON file."""
        self.storage.save_data(self.students, self.courses, self.faculty)


def run_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    """Initializes and runs the EduTrack Web server."""
    storage = DataStorage()
    raw = storage.load_data()
    raw_students = raw.get("students", {})
    raw_courses = raw.get("courses", {})
    raw_faculty = raw.get("faculty", {})

    if not raw_students and not raw_courses:
        f_seed, c_seed, s_seed = generate_seed_data()
        students = s_seed
        courses = c_seed
        faculty = f_seed
        storage.save_data(students, courses, faculty)
    else:
        students = {reg: Student.from_dict(d) for reg, d in raw_students.items()}
        courses = {code: Course.from_dict(d) for code, d in raw_courses.items()}
        faculty = {eid: Faculty.from_dict(d) for eid, d in raw_faculty.items()}

    # Initialize Services
    EduTrackApiHandler.storage = storage
    EduTrackApiHandler.students = students
    EduTrackApiHandler.courses = courses
    EduTrackApiHandler.faculty = faculty
    EduTrackApiHandler.student_svc = StudentService(students)
    EduTrackApiHandler.course_svc = CourseService(courses, students)
    EduTrackApiHandler.attendance_svc = AttendanceService(students)
    EduTrackApiHandler.analytics_svc = AnalyticsService(students, courses)

    # Attempt to bind to requested port or next available
    server = None
    for p in range(port, port + 10):
        try:
            server = ThreadedHTTPServer((host, p), EduTrackApiHandler)
            port = p
            break
        except OSError:
            continue

    if not server:
        print(f"[Error] Could not bind to port in range {port}-{port+10}")
        sys.exit(1)

    url = f"http://{host}:{port}"
    print("=" * 68)
    print(f"       EDUTRACK v{__version__} - MODERN ACADEMIC & ATTENDANCE WEB UI")
    print("=" * 68)
    print(f" [*] Server running at: {url}")
    print(f" [*] Students: {len(students)} | Courses: {len(courses)}")
    print(f" [*] Zero external dependencies - Powered by Python Standard Library")
    print(" [*] Press Ctrl+C anytime to stop the server")
    print("=" * 68 + "\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Shutting down EduTrack Web Server...]")
        server.server_close()


if __name__ == "__main__":
    run_server()
