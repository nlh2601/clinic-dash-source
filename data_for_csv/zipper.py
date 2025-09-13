import pandas as pd

# STEP 1: Load your file
input_file = "native_pop.csv"  # <-- Replace with your actual filename
df = pd.read_csv(input_file)

# STEP 2: Mapping PCSA names to ZIP codes
pcsa_to_zip = {
    "Airport - Moanalua": 96819,
    "Ala Moana - Nu‘uanu": 96813,
    "Downtown - Kalihi": 96817,
    "Ewa - Kalaeloa": 96706,
    "Hamakua": 96727,
    "Hanalei": 96714,
    "Hawaii Kai - Kaimuki": 96825,
    "Hickam - Pearl City": 96782,
    "Hilo": 96720,
    "Kapa‘a": 96746,
    "Kapolei - Makakilo": 96707,
    "Ka‘u": 96772,
    "Koloa": 96756,
    "Ko‘olauloa": 96762,
    "Ko‘olaupoko": 96744,
    "Lahaina": 96761,
    "Lihu‘e": 96766,
    "Makawao": 96768,
    "McCully - Makiki": 96826,
    "Mililani": 96789,
    "Moloka‘i": 96748,
    "North Kohala": 96755,
    "North Kona": 96740,
    "Puna": 96778,
    "South Kohala": 96738,
    "South Kona": 96704,
    "Wahiawa": 96786,
    "Waialua": 96791,
    "Waianae": 96792,
    "Waikiki - Palolo": 96815,
    "Wailuku": 96793,
    "Waimea": 96743,
    "Waipahu": 96797,
    "Hana": 96713,
    "Lana‘i": 96763,
    "Lanai": 96763  # fallback spelling
}


# STEP 3: Find PCSA rows
mask = df["Location Type"] == "Primary Care Service Area"

# STEP 4: Replace PCSA name with ZIP
df.loc[mask, "Location"] = df.loc[mask, "Location"].map(pcsa_to_zip)

# STEP 5: Update Location Type to "Zip Code"
df.loc[mask, "Location Type"] = "Zip Code"

# STEP 6: Save the updated file
output_file = "native_pop_zip.csv"
df.to_csv(output_file, index=False)

print("✅ Done! Replaced PCSAs with ZIP codes and updated Location Type.")
print(f"📁 Output saved as: {output_file}")
