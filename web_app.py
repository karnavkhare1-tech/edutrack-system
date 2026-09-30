"""EduTrack Web UI Entry Point.

Run this file to launch the modern web-based GUI:
    python web_app.py
"""

import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from edutrack.web.server import run_server

if __name__ == "__main__":
    run_server(host="127.0.0.1", port=8000, open_browser=True)
