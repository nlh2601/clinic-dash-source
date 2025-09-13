

# import pandas as pd
# import glob
# from collections import defaultdict

# # === CONFIGURATION ===

# # Folder with all your CSVs
# csv_files = glob.glob(r"C:\Users\nateh\OneDrive\Desktop\methodology\data_csvs\*.csv")

# # Define indicators you're interested in
# indicator_keywords = {
#     "% diabetes": "diabetes",
#     "% high blood pressure": "high blood pressure",
#     "% kidney disease": "kidney disease",
#     "% disability": "disability",
#     "% uninsured": "uninsured",
#     "% no doctor due to money": "no doctor",
#     "health equity index": "health equity index",
#     "# health centers": "health centers",
#     "# nonprofits": "nonprofits",
#     "clinics per 1,000 population": "clinics per 1,000",
#     "nonprofits per 1,000 population": "nonprofits per 1,000",
#     "% below poverty line": "poverty",
#     "% unemployed": "unemployed",
#     "% without vehicle access": "vehicle access",
#     "% age 65+": "age 65+",
#     "% BIPOC or % Native Hawaiian/Pacific Islander": "bipoc",
#     "% limited English proficiency": "limited english",
#     "chronic burden index": "chronic burden index",
#     "access barrier score": "access barrier score",
#     "risk growth index": "risk growth index",
#     "clinic shortage flag": "clinic shortage flag"
# }

# # Store data by ZIP and year+indicator
# data_by_zip = defaultdict(lambda: defaultdict(dict))

# # === PROCESS CSV FILES ===

# for file in csv_files:
#     df = pd.read_csv(file)
#     df.columns = [col.strip() for col in df.columns]  # Normalize column headers

#     for _, row in df.iterrows():
#         location_type = str(row.get("Location Type", "")).strip().lower()
#         if location_type != "zip code":
#             continue  # Skip non-ZIP Code entries

#         zip_code = str(row.get("Location", "")).strip()
#         indicator = str(row.get("Indicator Name", "")).strip().lower()
#         year = str(row.get("Period of Measure", "")).strip()
#         rate = row.get("Indicator Rate Value", None)

#         for colname, keyword in indicator_keywords.items():
#             if keyword in indicator:
#                 column_key = f"{colname}_{year}"
#                 try:
#                     data_by_zip[zip_code][column_key] = float(rate)
#                 except:
#                     continue

# # === BUILD FINAL DATAFRAME ===

# flat_data = []

# for zip_code, year_data in data_by_zip.items():
#     row = {"zip": zip_code}
#     row.update(year_data)
#     flat_data.append(row)

# result_df = pd.DataFrame(flat_data)

# # === EXPORT ===

# result_df = result_df.sort_values("zip")
# result_df.to_csv("consolidated_zip_health_data.csv", index=False)
# print("✅ CSV created: consolidated_zip_health_data.csv")

import pandas as pd
import glob
import os
import re
from collections import defaultdict

# ---------- CONFIG ---------- #
folder_path = r"C:\Users\nateh\OneDrive\Desktop\methodology\data_csvs"
csv_files   = glob.glob(os.path.join(folder_path, "*.csv"))

INDEX_FILE_COLS = {"Zip Code", "Index"}
DETAILED_REQ_COLS = {
    "Indicator Name",
    "Location Type",
    "Location",
    "Period of Measure",
    "Indicator Rate Value"
}
SLOPE_COLS = {
    "zip", "diabetes_slope", "disabled_slope", "employed_slope",
    "healthindex_slope", "hibp_slope", "kidney_slope",
    "bipoc_slope", "nodoc_slope"
}
indicator_keywords = {
    "diabetes":                     "diabetes",
    "high blood pressure":          "high blood pressure",
    "kidney disease":               "kidney disease",
    "disability":                   "disability",
    "uninsured":                    "uninsured",
    "did not see a doctor":         "no doctor",
    "health center":                "health centers",
    "nonprofit":                    "nonprofits",
    "clinic per 1,000":             "clinics per 1,000",
    "nonprofit per 1,000":          "nonprofits per 1,000",
    "poverty":                      "poverty",
    "unemployed":                   "unemployed",
    "civilian labor force":         "employed",
    "without vehicle":              "vehicle access",
    "65+":                          "age 65+",
    "native hawaiian":              "bipoc",
    "pacific islander":             "bipoc",
    "limited english":              "limited english",
    "chronic burden":               "chronic burden index",
    "access barrier":               "access barrier score",
    "risk growth":                  "risk growth index",
    "clinic shortage":              "clinic shortage flag",
    "health equity index":          "index"
}

# ---------- HELPERS ---------- #
def year_from_filename(path: str) -> str | None:
    m = re.search(r"20\d{2}", os.path.basename(path))
    return m.group(0) if m else None

def clean_zip(z) -> str | None:
    try:
        return str(int(float(z))).zfill(5)
    except:
        return None

# ---------- MAIN ---------- #
data_by_zip = defaultdict(dict)

for file in csv_files:
    try:
        df = pd.read_csv(file)
        df.columns = [c.strip() for c in df.columns]
    except Exception:
        try:
            df = pd.read_csv(file, header=2)
            df.columns = [c.strip() for c in df.columns]
        except Exception:
            continue  # Skip unreadable file

    cols = set(df.columns)

    # ---- 1) SIMPLE ZIP-INDEX FILE ---- #
    if INDEX_FILE_COLS.issubset(cols):
        yr = year_from_filename(file)
        if yr is None:
            continue
        for _, row in df.iterrows():
            z = clean_zip(row["Zip Code"])
            if z:
                data_by_zip[z][f"Index_{yr}"] = row.get("Index", None)
        continue

    # ---- 2) DETAILED INDICATOR FILE ---- #
    if DETAILED_REQ_COLS.issubset(cols):
        for _, row in df.iterrows():
            if str(row["Location Type"]).strip().lower() != "zip code":
                continue

            z = clean_zip(row["Location"])
            yr = str(row["Period of Measure"]).strip()
            rate = row["Indicator Rate Value"]
            ind  = str(row["Indicator Name"]).strip().lower()

            if not z:
                continue

            if "health equity index" in ind:
                data_by_zip[z][f"index_{yr}"] = rate
                continue

            for key, slug in indicator_keywords.items():
                if key in ind:
                    data_by_zip[z][f"{slug}_{yr}"] = rate
                    break
        continue

    # ---- 3) SLOPE DATA FILE ---- #
    lower_cols = {c.strip().lower() for c in df.columns}
    if SLOPE_COLS.issubset(lower_cols):
        df.columns = [c.strip().lower() for c in df.columns]
        for _, row in df.iterrows():
            z = clean_zip(row["zip"])
            if not z:
                continue
            for col in SLOPE_COLS - {"zip"}:
                data_by_zip[z][col] = row[col]
        print(f"✅ Slope data merged from: {file}")
        continue

# ---------- BUILD FINAL CSV ---------- #
rows = [{"zip": z, **vals} for z, vals in data_by_zip.items()]
final_df = pd.DataFrame(rows).sort_values("zip")

out_path = os.path.join(folder_path, "combined_all_zip_data.csv")
final_df.to_csv(out_path, index=False)
print(f"✅ Combined file written to: {out_path}")
# End of csv_combiner.py 

