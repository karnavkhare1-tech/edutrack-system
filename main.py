"""EduTrack - Student Academic Performance & Attendance Monitoring System.

Main application entry point.
"""

import sys
from edutrack.storage.file_storage import DataStorage
from edutrack.cli.menu import EduTrackCLI


def main():
    """Initializes and runs the EduTrack CLI application."""
    try:
        storage = DataStorage()
        app = EduTrackCLI(storage=storage)
        app.start()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user. Exiting safely...")
        sys.exit(0)


if __name__ == "__main__":
    main()
