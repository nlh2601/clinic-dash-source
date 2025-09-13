import pandas as pd

# Load the Excel file
excel_file = 'organized_matched_nonprofits.xlsx'
df = pd.read_excel(excel_file)  # Reads the first sheet by default

# Save as CSV
csv_file = 'organized_matched_nonprofits.csv'
df.to_csv(csv_file, index=False)

print(f"Converted {excel_file} to {csv_file}")
