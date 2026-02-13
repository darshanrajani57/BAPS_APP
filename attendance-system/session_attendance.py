import json
import uuid
from datetime import datetime

SESSION_FILE = "attendance-system/data/sessions.json"
ATTENDANCE_FILE = "attendance-system/data/attendance.json"

# ---------- Helpers ----------
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- Create Session ----------
def create_session(date, start_time, end_time):
    sessions = load_json(SESSION_FILE)

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "created_at": datetime.now().isoformat()
    }

    save_json(SESSION_FILE, sessions)
    print("Session created:", session_id)
    return session_id

# ---------- Mark Attendance ----------
def mark_attendance(session_id, person_name, status):
    attendance = load_json(ATTENDANCE_FILE)

    attendance.setdefault(session_id, {})
    attendance[session_id][person_name] = status

    save_json(ATTENDANCE_FILE, attendance)
    print(f"Marked {person_name} as {status}")

# ---------- TEST FLOW ----------
session_id = create_session(
    date="2026-01-19",
    start_time="18:00",
    end_time="19:30"
)

mark_attendance(session_id, "Dhruval Bipinbhai Patel", "Present")
mark_attendance(session_id, "Jay Vipulbhai Patel", "Absent")
