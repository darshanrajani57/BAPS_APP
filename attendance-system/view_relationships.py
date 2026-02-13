import json

ASSIGNMENT_FILE = "attendance-system/data/assignments.json"

def load_assignments():
    try:
        with open(ASSIGNMENT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# -------- View Sampark for a Yuvak --------
def get_sampark_for_yuvak(yuvak_name):
    assignments = load_assignments()
    record = assignments.get(yuvak_name)

    if record:
        return record["sampark"]
    return None

# -------- View Yuvaks under a Sampark --------
def get_yuvaks_for_sampark(sampark_name):
    assignments = load_assignments()
    return [
        yuvak
        for yuvak, record in assignments.items()
        if record["sampark"] == sampark_name
    ]


# -------- TEST CASES --------
yuvak_name = "Dhruval Bipinbhai Patel"
sampark_name = "Jay Vipulbhai Patel"

print("Viewing from Yuvak side:")
print("Yuvak:", yuvak_name)
print("Assigned Sampark:", get_sampark_for_yuvak(yuvak_name))

print("\nViewing from Sampark side:")
print("Sampark:", sampark_name)
print("Assigned Yuvaks:", get_yuvaks_for_sampark(sampark_name))
