import pandas as pd

# Read the original CSV
df = pd.read_csv("lead_evaluation_input.csv")

# Fields that should be passed to your automation
required_fields = [
    "company_name",
    "website",
    "industry",
    "email",
    "company_size",
    "location",
    "lead_description"
]

# Keep only the required fields
input_df = df[required_fields]

# Save as a new CSV
input_df.to_csv("input.csv", index=False)

print(f"Created input.csv with {len(input_df)} leads.")
print("Fields included:")
print(input_df.columns.tolist())