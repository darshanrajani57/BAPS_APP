import json
import pandas as pd

SESSION_FILE = "attendance-system/data/sessions.json"
ATTENDANCE_FILE = "attendance-system/data/attendance.json"
EXCEL_FILE = "attendance-system/data/raw_excel/Book1_baps.xlsx"

TARGET_MONTH = "2026-01"  # YYYY-MM

# Load data
sessions = json.load(open(SESSION_FILE))
attendance = json.load(open(ATTENDANCE_FILE))
df = pd.read_excel(EXCEL_FILE)

# Filter sessions by month
monthly_sessions = {
    sid: s for sid, s in sessions.items()
    if s["date"].startswith(TARGET_MONTH)
}

print("\n====== MONTHLY REPORT ======")
print("Month:", TARGET_MONTH)
print("Total Sessions:", len(monthly_sessions))
print("-" * 50)

# Prepare attendance aggregation
stats = {}

for sid in monthly_sessions:
    session_att = attendance.get(sid, {})
    for _, row in df.iterrows():
        name = row["Yuvak Name"]
        role = row["Type"]

        stats.setdefault(name, {
            "role": role,
            "present": 0,
            "absent": 0
        })

        status = session_att.get(name, "Absent")
        if status == "Present":
            stats[name]["present"] += 1
        else:
            stats[name]["absent"] += 1

# Convert to DataFrame
report_df = pd.DataFrame.from_dict(stats, orient="index")

# Yuvak Summary
yuvaks = report_df[report_df["role"].str.lower() == "yuvak"]

print("\n--- YUVAK MONTHLY SUMMARY ---")
print("Total Yuvaks:", len(yuvaks))
print("Total Presents:", yuvaks["present"].sum())
print("Total Absents:", yuvaks["absent"].sum())

# Role-wise Summary
for role in ["sampark karyakar", "karyakar", "sanchalak"]:
    subset = report_df[report_df["role"].str.lower() == role]
    print(f"\n--- {role.upper()} MONTHLY SUMMARY ---")
    print("Members:", len(subset))
    print("Total Presents:", subset["present"].sum())
    print("Total Absents:", subset["absent"].sum())
