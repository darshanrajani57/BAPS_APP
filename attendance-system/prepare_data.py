import pandas as pd

file_path = "attendance-system/data/raw_excel/Book1_baps.xlsx"
df = pd.read_excel(file_path)

print("DATA PREPARATION (NO CLEANING)\n")

# Just checking availability for logic
print("Records with address available:",
      df["Yuvak Address"].notna().sum())

print("Records with DOB available:",
      df["DOB"].notna().sum())

print("\nSample raw records:")
print(
    df[
        [
            "Yuvak Name",
            "Type",
            "Yuvak Address",
            "DOB"
        ]
    ].head(5)
)
