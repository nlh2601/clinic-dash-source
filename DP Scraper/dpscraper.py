import requests
import pandas as pd
import time

API_KEY = "API_KEY_HERE" # Replace with Api Key

# Trimmed list for reliability across 2020–2022
variables = {
    "DP03_0062E": "Median_Household_Income",
    "DP03_0009PE": "Unemployment_Rate_Pct",
    "DP05_0024PE": "Pct_Over_65",
    "DP05_0071PE": "Pct_Native_Hawaiian_PI",
    "DP05_0001E": "Total_Population"
}

years = list(range(2016, 2023))  # 2016–2022

for year in years:
    print(f"\n📅 Year: {year}")
    try:
        # Check if variables exist
        check_url = f"https://api.census.gov/data/{year}/acs/acs5/profile/groups/DP03.json"
        check_response = requests.get(check_url)
        check_response.raise_for_status()
        available_vars = set(check_response.json()['variables'].keys())

        # Drop any variables not available this year
        active_vars = {k: v for k, v in variables.items() if k in available_vars}

        if not active_vars:
            print(f"⚠️ No valid variables for {year}. Skipping...")
            continue

        fields = ",".join(["NAME"] + list(active_vars.keys()))
        data_url = f"https://api.census.gov/data/{year}/acs/acs5/profile?get={fields}&for=zip%20code%20tabulation%20area:*&in=state:15&key={API_KEY}"

        response = requests.get(data_url)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data[1:], columns=data[0])
        df.rename(columns=active_vars, inplace=True)
        df["Year"] = year
        df.to_csv(f"hawaii_dp_core_{year}.csv", index=False)
        print(f"✅ Saved hawaii_dp_core_{year}.csv")

        time.sleep(1)

    except Exception as e:
        print(f"❌ Failed for {year}: {e}")

