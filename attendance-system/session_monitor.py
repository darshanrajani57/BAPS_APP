import json
from datetime import datetime
import subprocess
import sys

SESSION_FILE = "attendance-system/data/sessions.json"

def load_sessions():
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

sessions = load_sessions()
now = datetime.now()

updated = False

for session_id, session in sessions.items():
    if session.get("processed"):
        continue

    end_time_str = f"{session['date']} {session['end_time']}"
    end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")

    if now >= end_time:
        print(f"Session ended: {session_id}")
        print("→ Locking attendance")
        print("→ Running absence logic\n")

        # Run absence logic
        subprocess.run(
            [sys.executable, "attendance-system/absence_logic.py"]
        )

        session["processed"] = True
        updated = True

if updated:
    save_sessions(sessions)
    print("\nSession processing completed.")
else:
    print("No sessions to process.")
