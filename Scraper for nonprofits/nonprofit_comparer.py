import pandas as pd

# === File paths ===
hawaii_file = 'hawaii_nonprofit_names_without.csv'
compare_file = 'eo_hi.csv'
output_file = 'organized_matched_nonprofits.xlsx'

# === Step 1: Load Hawaii nonprofit names and clean ===
hawaii_names = pd.read_csv(hawaii_file, header=None).stack().str.strip().str.upper().dropna().unique()

# === Step 2: Load EO file with correct column headers ===
eo_headers = [
    "EIN", "NAME", "ICO", "STREET", "CITY", "STATE", "ZIP", "GROUP", "SUBSECTION",
    "AFFILIATION", "CLASSIFICATION", "RULING", "DEDUCTIBILITY", "FOUNDATION",
    "ACTIVITY", "ORGANIZATION", "STATUS", "TAX_PERIOD", "ASSET_CD", "INCOME_CD",
    "FILING_REQ_CD", "PF_FILING_REQ_CD", "ACCT_PD", "ASSET_AMT", "INCOME_AMT",
    "REVENUE_AMT", "NTEE_CD", "SORT_NAME"
]
compare_df = pd.read_csv(compare_file, dtype=str, names=eo_headers, header=0).fillna('')

# === Step 3: Match names and build output ===
matched_rows = []

for name in hawaii_names:
    found = False
    for _, row in compare_df.iterrows():
        if any(name in str(cell).upper() for cell in row):
            matched_rows.append([name] + row.tolist())
            found = True
            break
    if not found:
        matched_rows.append([name] + ['NOT FOUND'])

# === Step 4: Set final headers and export ===
final_headers = ['Hawaii Nonprofit Name'] + eo_headers
output_df = pd.DataFrame(matched_rows, columns=final_headers[:len(matched_rows[0])])

# Save to Excel
output_df.to_excel(output_file, index=False)
print(f"✅ Excel file created: {output_file}")
