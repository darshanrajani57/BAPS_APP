import json
import datetime

ASSIGNMENT_FILE = "attendance-system/data/assignments.json"

def load_assignments():
    try:
        with open(ASSIGNMENT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_assignments(data):
    with open(ASSIGNMENT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def assign_yuvak(yuvak_name, sampark_name):
    assignments = load_assignments()

    assignments[yuvak_name] = {
        "sampark": sampark_name,
        "assigned_at": datetime.datetime.now().isoformat()
    }

    save_assignments(assignments)
    print(f"Assigned '{yuvak_name}' → '{sampark_name}'")

def sampark_workload():
    assignments = load_assignments()
    workload = {}

    for record in assignments.values():
        sp = record["sampark"]
        workload[sp] = workload.get(sp, 0) + 1

    return workload


# -------- TEST ASSIGNMENT --------
yuvak_name = "Dhruval Bipinbhai Patel"
sampark_name = "Jay Vipulbhai Patel"

assign_yuvak(yuvak_name, sampark_name)

print("\nCurrent Sampark Workload:")
for k, v in sampark_workload().items():
    print(k, ":", v)
