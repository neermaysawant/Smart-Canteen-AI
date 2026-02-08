import sqlite3
import os
import pandas as pd
import pickle
import json
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import mean_squared_error


# Database and Model Paths

base_dir = os.path.dirname(os.path.dirname(__file__))

db_path = os.path.join(base_dir, 'database', 'canteen.db')

models_dir = os.path.join(base_dir, 'models')

os.makedirs(models_dir, exist_ok=True)


# LOAD DATA FROM SQL

conn = sqlite3.connect(db_path)

df = pd.read_sql_query("SELECT * FROM canteen_data", conn)

conn.close()
if df.empty:
    raise ValueError("Database has no data. Run generate_data.py first.")
print("Data loaded:", df.shape)

if df.empty:
    raise ValueError("Database is empty. Please insert data first.")


# Features and Target

X = df[["day_of_week", "category", "menu_item", "is_exam_period"]]

y = df["plates_consumed"]


# categorical columns

categorical_features = ["day_of_week", "category", "menu_item"]


# Preprocessing

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"
)


# Model Names

models = {
    "LinearRegression": LinearRegression(),
    "DecisionTree": DecisionTreeRegressor(random_state=42),
    "RandomForest": RandomForestRegressor(random_state=42)
}


# train/test split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


best_model = None
best_rmse = float("inf")
best_name = ""

results = []

# Model Training and evaluation

for name, model in models.items():

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5

    print(f"{name} RMSE:", rmse)

    results.append((name, rmse))

    if rmse < best_rmse:
        best_rmse = rmse
        best_model = pipeline
        best_name = name


# Model Versioning

existing_models = [
    f for f in os.listdir(models_dir)
    if f.startswith("model_v") and f.endswith(".pkl")
]

version = len(existing_models) + 1

model_path = os.path.join(models_dir, f"model_v{version}.pkl")

metadata_path = os.path.join(models_dir, f"model_v{version}_metadata.json")


# Best model saving

with open(model_path, "wb") as f:
    pickle.dump(best_model, f)


# Metadata saving

metadata = {
    "model_name": best_name,
    "rmse": float(best_rmse),
    "trained_at": str(pd.Timestamp.now()),
    "version": version,
}

with open(metadata_path, "w") as f:

    json.dump(metadata, f)


print("================================")

print("Best model:", best_name)

print("RMSE:", best_rmse)

print("Model version saved:", version)

print("================================")
