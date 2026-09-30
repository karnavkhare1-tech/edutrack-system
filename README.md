# EduTrack: Student Academic Performance & Attendance Monitoring System

A clean and user-friendly Academic Performance and Attendance Management System that helps university students and faculty manage student records, course enrollments, attendance, academic marks, GPA calculations, and reports.

## Features

- Manage student profiles and course records
- Add, search, update, and remove students
- Manage course offerings, credits, instructors, slots, and seat capacities
- Enroll and drop courses with capacity validation
- Track student attendance and check the mandatory 75% attendance rule
- Calculate attendance recovery requirements and safe absence limits
- Maintain a debarred-student registry
- Record quizzes, assignments, midterms, and final examination marks
- Automatically calculate grades and semester GPA
- Generate course performance statistics and grade distributions
- Maintain a Dean's Honor Roll based on GPA
- Store application data using JSON
- Export student and attendance reports as CSV files
- Includes automated unit tests for models, services, validation, and GPA calculations

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/karnavkhare1-tech/edutrack-system.git
    ```

2. Navigate to the project directory:
    ```bash
    cd edutrack-system
    ```

3. Make sure Python 3.8 or higher is installed.

4. No third-party Python packages are required because the project uses the Python Standard Library.

## Usage

Start the main application:

```bash
python main.py
```

To run the automated demonstration:

```bash
python demo.py
```

The demo showcases the application's main workflows and generates sample CSV reports.

## Technologies Used

- Python 3.8+
- Object-Oriented Programming (OOP)
- Python `json` for data persistence
- Python `csv` for report generation
- Python `re` for input validation
- Custom exception handling
- Python `unittest` for automated testing
- Dictionaries, lists, tuples, and sets for data management

## Project Structure

```text
edutrack-system/
├── edutrack/
│   ├── models/
│   ├── services/
│   ├── storage/
│   ├── utils/
│   └── cli/
├── tests/
├── data/
├── reports/
├── main.py
├── demo.py
├── statement.md
├── PROJECT_REPORT.md
└── README.md
```

## Testing

Run the complete test suite using:

```bash
python -m unittest discover -s tests
```

The project includes tests for:

- Domain models
- GPA calculations
- Student and course workflows
- Attendance rules
- Input validation
- Edge cases and invalid data

## Sample Output

### Main Application

```text
=================================================================
       EDUTRACK - ACADEMIC & ATTENDANCE MANAGEMENT SYSTEM
        Empowering Student Success & Institutional Insights
=================================================================
 Registered Students: 5 | Active Courses: 4
=================================================================
1. Student Management (Add, View, Update, Delete)
2. Course Catalog & Enrollments
3. Attendance Tracking & 75% Rule Compliance
4. Academic Marks, GPA & Performance Analytics
5. Export Reports & Data Management (CSV Export)
0. Save & Exit
-----------------------------------------------------------------
Select an option [0-5]:
```

### GPA Calculation

EduTrack calculates the semester GPA using credit-weighted grade points:

```text
GPA = Σ(Grade Point × Credits) / Σ(Credits)
```

### Attendance Monitoring

The system checks the 75% attendance requirement and provides guidance based on the student's current attendance status.

```text
Course: CSE1001
Attended: 20/30
Attendance: 66.67%
Status: DEBARRED (<75%)

Advice: Must attend upcoming classes to regain eligibility.
```

## Screenshots

Add screenshots of the EduTrack application here:

```text
![EduTrack Screenshot](screenshot.png)
```

## License

This project is open-source and developed for academic evaluation under the MIT License.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request for improvements, bug fixes, or new features.
