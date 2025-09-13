import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error
from math import sqrt

# Load CSVs
actuals_df = pd.read_csv("generated.csv")  # contains Zip Code, Index, Rank, County
preds_df = pd.read_csv("index_2025_predictions.csv")  # contains zip, predicted_index_2025

# Prep ZIP codes
actuals_df["zip"] = actuals_df["Zip Code"].astype(str).str.zfill(5)
preds_df["zip"] = preds_df["zip"].astype(str).str.zfill(5)

# Rename for clarity
actuals_df = actuals_df.rename(columns={"Index": "actual_index"})
preds_df = preds_df.rename(columns={"predicted_index_2025": "predicted_index"})

# Merge datasets on ZIP, only keeping matches
merged = pd.merge(actuals_df[["zip", "actual_index"]], 
                  preds_df[["zip", "predicted_index"]],
                  on="zip", how="inner")

# Drop any missing data
merged = merged.dropna(subset=["actual_index", "predicted_index"])

# Compute metrics
y_true = merged["actual_index"]
y_pred = merged["predicted_index"]

r2 = r2_score(y_true, y_pred)
rmse = sqrt(mean_squared_error(y_true, y_pred))

# 🎯 Print results
print("\n📈 Model Accuracy Report")
print("-" * 40)
print(f"✅ ZIPs Compared:    {len(merged)}")
print(f"🎯 R² Score:         {r2:.4f}")
print(f"📉 RMSE:             {rmse:.2f}")
print("-" * 40)
