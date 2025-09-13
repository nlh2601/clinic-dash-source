import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
import folium
import branca.colormap as cm
import json

# ----------------------------- CONFIG ----------------------------------
BASE_YEAR = 2024
PREDICT_YEAR = 2025

BASE_DIR = r"C:\Users\nateh\OneDrive\Desktop\methodology\xgboost"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "combined_all_zip_data.csv")
GEOJSON_PATH = os.path.join(DATA_DIR, "hi_hawaii_zip_codes_geo.min.json")

# ----------------------------- LOAD & PREP DATA ------------------------
df = pd.read_csv(CSV_PATH)
df["zip"] = df["zip"].astype(str).str.zfill(5)

slope_cols = [c for c in df.columns if c.endswith("_slope")]
year_cols = [c for c in df.columns if c.endswith(f"_{BASE_YEAR}")]
predictors = slope_cols + year_cols

target_col_name = f"Index_{BASE_YEAR + 1}"
if target_col_name in df.columns:
    target = target_col_name
else:
    target = f"Index_{BASE_YEAR}"
    print(f"\u26a0\ufe0f Warning: Target column '{target_col_name}' not found, using '{target}' instead.")

df_model = df.dropna(subset=predictors + [target])
X = df_model[predictors]
y = df_model[target]

# ----------------------------- TRAIN MODEL -----------------------------
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
rmse = sqrt(mean_squared_error(y_test, y_pred))
print(f"✅ Model trained. RMSE: {rmse:.2f}")

# ----------------------------- PREDICT FUTURE --------------------------
df_future = df.copy()
years_ahead = PREDICT_YEAR - BASE_YEAR

feature_map_future = {
    col: col.replace(f"_{BASE_YEAR}", f"_{PREDICT_YEAR}")
    for col in year_cols if col.replace(f"_{BASE_YEAR}", "_slope") in df.columns
}

for base_col, future_col in feature_map_future.items():
    slope_col = base_col.replace(f"_{BASE_YEAR}", "_slope")
    df_future[future_col] = df_future[base_col] + years_ahead * df_future[slope_col]

future_X = df_future[slope_cols].copy()
for base_col, future_col in feature_map_future.items():
    future_X[base_col] = df_future[future_col]

for col in year_cols:
    if col in predictors:
        future_X[col] = df_future[col]

future_X = future_X.fillna(0)
df_future = df_future.loc[future_X.index]
df_future[f"predicted_index_{PREDICT_YEAR}"] = model.predict(future_X)
print(f"✅ Predictions generated for Index_{PREDICT_YEAR}")

# ----------------------------- SAVE RESULTS ----------------------------
pred_csv = os.path.join(OUTPUT_DIR, f"index_{PREDICT_YEAR}_predictions.csv")
df_future[["zip", f"predicted_index_{PREDICT_YEAR}"]].to_csv(pred_csv, index=False)
print(f"📄 Saved predictions to: {pred_csv}")

# ----------------------------- LOAD GEOJSON ----------------------------
geo = gpd.read_file(GEOJSON_PATH)
geo["zip"] = geo["ZCTA5CE10"].astype(str).str.zfill(5)

# Merge ZIP-level predictions into the GeoDataFrame
merged = geo.merge(df_future[["zip", f"predicted_index_{PREDICT_YEAR}"]], on="zip", how="left")

# ----------------------------- STATIC MAP ------------------------------
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
vmin = merged[f"predicted_index_{PREDICT_YEAR}"].min()
vmax = merged[f"predicted_index_{PREDICT_YEAR}"].max()

merged.plot(
    column=f"predicted_index_{PREDICT_YEAR}",
    cmap="Reds_r",
    linewidth=0.6,
    edgecolor="black",
    legend=True,
    legend_kwds={
        'label': f"Predicted Health Equity Index ({PREDICT_YEAR})",
        'shrink': 0.6
    },
    missing_kwds={"color": "white", "label": "No data"},
    ax=ax,
)
ax.set_title(f"Health Equity Index by ZIP ({PREDICT_YEAR}) — Red = Worse Access", fontsize=15)
ax.axis("off")

map_png = os.path.join(OUTPUT_DIR, f"predicted_index_map_{PREDICT_YEAR}.png")
plt.savefig(map_png, dpi=300, bbox_inches="tight")
print(f"🗘️ Saved static map image to: {map_png}")
plt.close()

# ----------------------------- INTERACTIVE MAP -------------------------
merged = merged.to_crs("EPSG:4326")
bounds = merged.total_bounds
center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

index_col = f"predicted_index_{PREDICT_YEAR}"
vmin = merged[index_col].min()
vmax = merged[index_col].max()

colormap = cm.LinearColormap(
    colors=["#ffffff", "#ffcccc", "#ff9999", "#ff6666", "#cc0000"],
    vmin=vmin,
    vmax=vmax,
    caption=f"Health Equity Index ({PREDICT_YEAR}) - An Estimated Map of Hawaii"
)

m = folium.Map(location=center, zoom_start=7, tiles="cartodbpositron")
geojson_data = json.loads(merged.to_json())

def style_function(feature):
    value = feature["properties"].get(index_col)
    return {
        "fillColor": colormap(value) if value is not None else "lightgray",
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7 if value is not None else 0.4,
    }

folium.GeoJson(
    geojson_data,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["zip", index_col],
        aliases=["ZIP Code", "Predicted Index"],
        localize=True,
        sticky=True
    )
).add_to(m)

colormap.add_to(m)

html_map = os.path.join(OUTPUT_DIR, f"interactive_predicted_index_map_{PREDICT_YEAR}.html")
m.save(html_map)
print(f"🗽 Saved interactive map to: {html_map}")