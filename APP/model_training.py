# model_training.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

# -----------------------------
# Load dataset
# -----------------------------
data_path = "./data/oebb_gtfs/stop_times_geo_with_startEnd_calc.csv"
df = pd.read_csv(data_path)

# -----------------------------
# Select relevant features
# -----------------------------
cols_needed = [
    "distance",           # distance between stops (km)
    "speed",              # avg segment speed (km/h)
    "estimated_weight_t", # estimated train weight (tons)
    "weekly_total",       # number of weekly trips
    "EPI_segment"         # target variable
]

df = df[cols_needed].dropna()

# -----------------------------
# Define features and target
# -----------------------------
X = df[["distance", "speed", "estimated_weight_t", "weekly_total"]]
y = df["EPI_segment"]

# -----------------------------
# Split into train/test sets
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# Train Linear Regression
# -----------------------------
lin_model = LinearRegression()
lin_model.fit(X_train, y_train)

y_pred_lin = lin_model.predict(X_test)
r2_lin = r2_score(y_test, y_pred_lin)
mae_lin = mean_absolute_error(y_test, y_pred_lin)

# -----------------------------
# Train Random Forest
# -----------------------------
rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
r2_rf = r2_score(y_test, y_pred_rf)
mae_rf = mean_absolute_error(y_test, y_pred_rf)

# -----------------------------
# Train XGBoost
# -----------------------------
xgb_model = xgb.XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
xgb_model.fit(X_train, y_train)

y_pred_xgb = xgb_model.predict(X_test)
r2_xgb = r2_score(y_test, y_pred_xgb)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)

# -----------------------------
# Compare Models
# -----------------------------
results = pd.DataFrame({
    "Model": ["Linear Regression", "Random Forest", "XGBoost"],
    "R² Score": [r2_lin, r2_rf, r2_xgb],
    "MAE": [mae_lin, mae_rf, mae_xgb]
})

print("\n Model Performance Comparison:")
print(results.to_string(index=False))

# -----------------------------
# Save all models
# -----------------------------
os.makedirs("./models", exist_ok=True)
joblib.dump(lin_model, "./models/epi_predictor_linear.pkl")
joblib.dump(rf_model, "./models/epi_predictor_rf.pkl")
joblib.dump(xgb_model, "./models/epi_predictor_xgb.pkl")

print("\n Models saved to ./models/")
