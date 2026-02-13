import json

ATTENDANCE_FILE = "attendance-system/data/attendance.json"
ASSIGNMENT_FILE = "attendance-system/data/assignments.json"

ADMIN_NAME = "ADMIN"

# ---------- Load Helpers ----------
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

attendance = load_json(ATTENDANCE_FILE)
assignments = load_json(ASSIGNMENT_FILE)

# ---------- Pick Latest Session ----------
latest_session_id = list(attendance.keys())[-1]
session_attendance = attendance[latest_session_id]

print("Analyzing session:", latest_session_id)
print("-" * 50)

# ---------- Identify Absentees ----------
absent_people = [
    name for name, status in session_attendance.items()
    if isinstance(status, dict) and status.get("status", "").lower() == "absent"
    or isinstance(status, str) and status.lower() == "absent"
]

print("Absent people:", absent_people)
print("-" * 50)

# ---------- Notifications ----------
admin_notifications = []
sampark_notifications = {}

for person in absent_people:
    # Case 1: Person is a Yuvak (exists in assignments)
    if person in assignments:
        sampark = assignments[person]["sampark"]

        # Notify Sampark ALWAYS
        sampark_notifications.setdefault(sampark, [])
        sampark_notifications[sampark].append(person)

        # Notify Admin ALWAYS
        admin_notifications.append(
            f"Yuvak '{person}' was absent (Assigned Sampark: {sampark})"
        )

    # Case 2: Person is Sampark or other role
    else:
        admin_notifications.append(
            f"'{person}' was absent (Role: Sampark/Karyakar/Admin)"
        )

# ---------- Print Notifications ----------
print("\n--- NOTIFICATIONS ---\n")

for sampark, yuvaks in sampark_notifications.items():
    print(f"Notify Sampark Karyakar: {sampark}")
    print("Absent Yuvaks:", yuvaks)
    print()

print("Notify ADMIN:")
for msg in admin_notifications:
    print("-", msg)
