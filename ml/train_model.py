import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# LOAD DATASET
# ============================================================

data = pd.read_csv("queue_data.csv")

print("Dataset loaded successfully!")
print(data.head())
print("\nColumns:")
print(data.columns.tolist())


# ============================================================
# CLEAN DATA
# ============================================================

data = data.dropna()


# ============================================================
# SELECT FEATURES
# ============================================================

X = data.drop(columns=["wait_time"])

y = data["wait_time"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ============================================================
# TRAIN RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(X_test)


# ============================================================
# MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("MAE:", mae)
print("MSE:", mse)
print("R2 Score:", r2)


# ============================================================
# SAVE TRAINED MODEL
# ============================================================

joblib.dump(model, "queue_model.pkl")

joblib.dump(
    list(X.columns),
    "model_features.pkl"
)

print("\n==============================")
print("MODEL SAVED SUCCESSFULLY")
print("==============================")

print("queue_model.pkl created")
print("model_features.pkl created")