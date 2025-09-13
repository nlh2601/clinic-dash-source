import os
import pandas as pd
import re

folder_path = "data_csvs"  # Replace with your folder name
combined = None

for filename in os.listdir(folder_path):
    if not filename.endswith(".csv"):
        continue

    match = re.search(r"(\d{4})", filename)
    if not match:
        print(f"Skipping invalid filename: {filename}")
        continue
    year = match.group(1)

    indicator_parts = filename.replace(".csv", "").split("_")
    if len(indicator_parts) < 2:
        print(f"Skipping filename with no indicator: {filename}")
        continue
    indicator_name = indicator_parts[1].lower()

    filepath = os.path.join(folder_path, filename)

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"⚠️ Error reading {filename}: {e}")
        try:
            # Print the first 5 lines of the file to help debug
            with open(filepath, 'r', encoding='utf-8') as f:
                print("Preview of file:")
                for _ in range(5):
                    print(f.readline().strip())
        except:
            print("Could not read file contents.")
        continue

    if "Location" not in df.columns or "Indicator Rate Value" not in df.columns:
        print(f"Skipping file with missing columns: {filename}")
        continue

    df["Year"] = int(year)
    df.rename(columns={"Indicator Rate Value": f"{indicator_name}_{year}"}, inplace=True)
    df = df[["Location", "Year", f"{indicator_name}_{year}"]]

    if combined is None:
        combined = df
    else:
        combined = pd.merge(combined, df, on=["Location", "Year"], how="outer")

if combined is not None:
    combined.to_csv("combined_health_data.csv", index=False)
    print("✅ Combined file saved as combined_health_data.csv")
else:
    print("⚠️ No data was combined. Please check your files.")
