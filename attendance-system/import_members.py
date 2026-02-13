import pandas as pd
import json

EXCEL_FILE = "C:\\Users\\Darshan\\Desktop\\BAPS_APP\\attendance-system\\data\\raw_excel\\Book1_baps.xlsx"
MEMBERS_FILE = "C:\\Users\\Darshan\\Desktop\\BAPS_APP\\attendance-system\\data\\members.json"

df = pd.read_excel(EXCEL_FILE)

members = {}

for _, row in df.iterrows():
    name = row["Yuvak Name"]

    members[name] = {
        "No": row.get("No"),
        "Category": row.get("Category"),
        "Type": row.get("Type"),
        "Yuvak Name": row.get("Yuvak Name"),
        "Yuvak Phone No.": row.get("Yuvak Phone No."),
        "Family Phone No.": row.get("Family Phone No."),
        "Yuvak Address": row.get("Yuvak Address"),
        "DOB": str(row.get("DOB")),
        "Status": row.get("Status", ""),
        "Study": row.get("Study"),
        "College Timing": row.get("College Timing", ""),
        "College Holiday": row.get("College Holiday", ""),
        "Job": row.get("Job"),
        "Job Timing": row.get("Job Timing", ""),
        "Job Holiday": row.get("Job Holiday", ""),
        "Last Updated": str(row.get("Last Updated")),
        "Remark": row.get("Remark")
    }

with open(MEMBERS_FILE, "w") as f:
    json.dump(members, f, indent=2)

print("✅ Members imported successfully")
print("Total members:", len(members))
