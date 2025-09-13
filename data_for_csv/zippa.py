import geopandas as gpd

# Point to the full shapefile path
shapefile_path = r"C:\Users\nateh\OneDrive\Desktop\methodology\tl_2020_us_zcta510\tl_2020_us_zcta510.shp"

# Load the full US ZCTA dataset (may take 5–15 seconds)
gdf = gpd.read_file(shapefile_path)

# Filter for Hawaii ZIPs (start with 967 or 968)
hi_gdf = gdf[gdf["ZCTA5CE10"].str.startswith(("967", "968"))].copy()
hi_gdf["zip"] = hi_gdf["ZCTA5CE10"]

# Save just the Hawaii ZIPs as GeoJSON
out_path = r"C:\Users\nateh\OneDrive\Desktop\methodology\xgboost\data\hi_zips_full.geojson"
hi_gdf.to_file(out_path, driver="GeoJSON")

print("✅ Saved full Hawaii ZIP GeoJSON to:")
print(out_path)
