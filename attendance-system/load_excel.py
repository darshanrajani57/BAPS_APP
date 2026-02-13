import pandas as pd

# Load Excel file
file_path = "attendance-system/data/raw_excel/Book1_baps.xlsx"
df = pd.read_excel(file_path)

# Show basic info
print("Total records:", len(df))
print("\nColumns:")
print(df.columns.tolist())

# Check role distribution
print("\nType value counts:")
print(df["Type"].value_counts())

# Separate roles
yuvaks = df[df["Type"].str.strip().str.lower() == "yuvak"]
sampark_karyakars = df[df["Type"].str.strip().str.lower() == "sampark karyakar"]

print("\nYuvak count:", len(yuvaks))
print("Sampark Karyakar count:", len(sampark_karyakars))

