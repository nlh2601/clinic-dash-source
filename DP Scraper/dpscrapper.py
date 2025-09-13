import requests
import pandas as pd
import time

API_KEY = "API_KEY_HERE" # replace with api key
variables = {
    "DP03_0062E": "Median_Household_Income",
    "DP03_0009PE": "Unemployment_Rate_Pct",
    "DP05_0024PE": "Pct_Over_65",
    "DP05_0071PE": "Pct_Native_Hawaiian_PI",
    "DP05_0001E": "Total_Population"
}

years = list(range(2016, 2023))  # All years you want

for year in years:
    print(f"\n📅 Year: {year}")
    try:
        base_url = f"https://api.census.gov/data/{year}/acs/acs5/profile"
        fields = ",".join(["NAME"] + list(variables.keys()))

        if year <= 2019:
            # Include state filter for years ≤2019
            url = f"{base_url}?get={fields}&for=zip%20code%20tabulation%20area:*&in=state:15&key={API_KEY}"
        else:
            # Omit state filter for 2020+
            url = f"{base_url}?get={fields}&for=zip%20code%20tabulation%20area:*&key={API_KEY}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data[1:], columns=data[0])
        df.rename(columns=variables, inplace=True)
        df["Year"] = year

        if year >= 2020:
            # Filter Hawai‘i ZIPs manually (ZIPs start with 967 or 968)
            df = df[df["zip code tabulation area"].str.startswith(("967", "968"))]

        df.to_csv(f"hawaii_dp03_dp05_{year}.csv", index=False)
        print(f"✅ Saved hawaii_dp03_dp05_{year}.csv")

        time.sleep(1)  # Respect API limits

    except Exception as e:
        print(f"❌ Failed for {year}: {e}")

