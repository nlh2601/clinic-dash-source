import pandas as pd

# Load the dataset
df = pd.read_csv('USHEALTHCENTERS.csv')

# Filter only for rows where the Site State Abbreviation is 'HI' (Hawaii)
hawaii_df = df[df['Site State Abbreviation'] == 'HI']

# Save the filtered data to a new CSV file
hawaii_df.to_csv('Hawaii_Health_Centers.csv', index=False)

print("✅ Filtered Hawaii data saved to 'Hawaii_Health_Centers.csv'")
