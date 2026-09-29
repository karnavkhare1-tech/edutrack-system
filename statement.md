# Project Statement: EduTrack - Academic Performance & Attendance Monitoring System

## 1. Problem Statement
In higher education institutions like VIT, students face rigorous continuous internal assessment systems coupled with strict regulatory guidelines, notably the mandatory minimum **75% attendance policy** to be eligible for end-semester examinations. Currently, students frequently lack real-time visibility into their cumulative attendance standing, struggle to predict how many upcoming classes they can safely miss or must attend to prevent debarment, and find it cumbersome to compute their weighted Grade Point Average (GPA) across multi-credit theory and lab courses. Simultaneously, course instructors and academic mentors spend substantial manual effort calculating course-wide performance distributions, tracking attendance deficits, and compiling tabular academic audits. There is a pressing need for a streamlined, reliable, and accessible academic management tool that automates attendance tracking, predicts margin buffers, computes weighted GPA, and produces analytical institution-grade reports.

## 2. Scope of the Project
EduTrack is designed as an all-in-one academic and attendance monitoring desktop/CLI application developed in Python. The project encapsulates:
- **Student Profile Management**: Complete registration, profile updates, and course enrollment workflows with strict registration format validation.
- **Course Administration**: Definition of courses with credits, faculty allocations, slots, and seat capacity controls.
- **Attendance & 75% Rule Compliance Engine**: Accurate logging of session-wise or cumulative attendance, automated calculation of attendance percentages, early-warning alerts for students at risk of debarment, and algorithmic calculations of classes needed to regain 75% eligibility.
- **Assessment & GPA Evaluation**: Recording multi-component assessment marks (Quizzes, Assignments, Midterms, Final Exam), relative/absolute grade point mapping (S, A, B, C, D, E, F), and credit-weighted Semester Grade Point Average (SGPA) computation.
- **Institutional Analytics & Data Export**: Aggregate course performance analysis (average, highest, lowest, pass rate, grade distribution histogram), Dean's Honor Roll leaderboard, and atomic export of structured audits to standard CSV spreadsheets.

## 3. Target Users
1. **University Students (First-Year Undergraduates)**: To monitor their attendance thresholds in real time, obtain recovery advice before reaching the debarment danger zone, and forecast their GPAs.
2. **Course Instructors & Faculty**: To quickly conduct session attendance, view seat capacities, evaluate internal test marks, and review grade distribution statistics.
3. **Academic Counselors & Faculty Advisors**: To identify struggling or debarred students across sections and export structured CSV reports for university administration.

## 4. High-Level Features
- **Student Information CRUD**: Register, search, view, update, and remove student profiles.
- **Course Catalog Management**: Offer courses, allocate slots and credit weightages, manage seat enrollments.
- **Automated Attendance Auditor**: Instant detection of students below 75% attendance with actionable recovery advice.
- **Grade & CGPA Calculator**: Credit-weighted calculation matching official 10-point university grading standards.
- **Academic Performance Analytics**: Class averages, pass rates, and visual grade distribution breakdown.
- **Dean's Honor Roll Leaderboard**: Dynamic ranking of top academic performers.
- **Data Persistence & Reporting**: Atomic JSON state persistence with instant CSV report generation for university audits.
