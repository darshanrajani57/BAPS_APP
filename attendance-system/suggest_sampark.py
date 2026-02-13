import pandas as pd
import re

file_path = "attendance-system/data/raw_excel/Book1_baps.xlsx"
df = pd.read_excel(file_path)

# -------- Helper for similarity (LOGICAL, NOT CLEANING) --------
def address_tokens(addr):
    if pd.isna(addr):
        return set()
    addr = addr.lower()
    addr = re.sub(r"[^a-z0-9\s]", " ", addr)
    return set(addr.split())

def similarity_score(addr1, addr2):
    t1 = address_tokens(addr1)
    t2 = address_tokens(addr2)
    if not t1 or not t2:
        return 0
    return len(t1 & t2)

# -------- Select ONE Yuvak for test --------
yuvak = df[df["Type"].str.lower() == "yuvak"].iloc[0]
yuvak_address = yuvak["Yuvak Address"]

print("Yuvak selected:")
print(yuvak["Yuvak Name"])
print("\nYuvak Address:")
print(yuvak_address)

# -------- Candidate Sampark Pool --------
sampark_pool = df[
    df["Type"].str.lower().isin(
        ["sampark karyakar", "karyakar", "sanchalak"]
    )
]

# -------- Compute Suggestions --------
suggestions = []

for _, row in sampark_pool.iterrows():
    score = similarity_score(yuvak_address, row["Yuvak Address"])
    suggestions.append({
        "Sampark Name": row["Yuvak Name"],
        "Type": row["Type"],
        "Score": score
    })

# -------- Sort & Show --------
suggestions = sorted(suggestions, key=lambda x: x["Score"], reverse=True)

print("\nTop Sampark Karyakar Suggestions:")
for s in suggestions[:5]:
    print(s)
