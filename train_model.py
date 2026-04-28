import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

# ================================
# LOAD DATA
# ================================
df = pd.read_csv("city_day.csv")

# ================================
# FIX DATE (IMPORTANT FIX ✅)
# ================================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Drop rows where date is invalid
df = df.dropna(subset=["Date"])

# Sort properly (VERY IMPORTANT)
df = df.sort_values(["City", "Date"])

# ================================
# CREATE FUTURE AQI TARGET
# ================================
df["AQI_next"] = df.groupby("City")["AQI"].shift(-1)

# ================================
# SELECT FEATURES
# ================================
FEATURES = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

# Keep only needed columns
df = df[FEATURES + ["AQI_next"]]

# ================================
# CLEAN DATA
# ================================
# Convert everything to numeric safely
for col in FEATURES + ["AQI_next"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop missing values
df = df.dropna()

print("✅ Clean dataset shape:", df.shape)

# ================================
# SPLIT DATA
# ================================
X = df[FEATURES]
y = df["AQI_next"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ================================
# SCALE FEATURES
# ================================
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ================================
# TRAIN MODEL
# ================================
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# ================================
# SAVE MODEL
# ================================
joblib.dump(model, "future_model.pkl")
joblib.dump(scaler, "future_scaler.pkl")

print("🎉 Model trained successfully!")
print("📁 Saved as future_model.pkl and future_scaler.pkl")