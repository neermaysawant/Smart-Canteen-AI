# -*- coding: utf-8 -*-
import sys
import io
# Force stdout to UTF-8 on Windows to prevent charmap encoding errors
# from ML libraries (LightGBM, CatBoost) that print Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

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

# Linear Models
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    BayesianRidge,
    HuberRegressor,
    SGDRegressor,
    PassiveAggressiveRegressor
)

# Tree Models
from sklearn.tree import DecisionTreeRegressor

# Ensemble Models
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    AdaBoostRegressor
)

# Support Vector Models
from sklearn.svm import SVR, LinearSVR

# Neighbors
from sklearn.neighbors import KNeighborsRegressor

# Kernel Methods
from sklearn.kernel_ridge import KernelRidge

# Gaussian Process
from sklearn.gaussian_process import GaussianProcessRegressor

# External Industry Models (install required)
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

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
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
    ],
    remainder="passthrough"
)


# Model Names

models = {

    # Linear Models
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(),
    "Lasso": Lasso(),
    "ElasticNet": ElasticNet(),
    "BayesianRidge": BayesianRidge(),
    "HuberRegressor": HuberRegressor(),
    "SGDRegressor": SGDRegressor(),
    "PassiveAggressiveRegressor": PassiveAggressiveRegressor(),

    # Tree-Based Models
    "DecisionTree": DecisionTreeRegressor(random_state=42),

    # Ensemble Tree Models
    "RandomForest": RandomForestRegressor(random_state=42),
    "ExtraTrees": ExtraTreesRegressor(random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
    "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
    "AdaBoost": AdaBoostRegressor(random_state=42),

    # Support Vector
    "SVR": SVR(),
    "LinearSVR": LinearSVR(),

    # Neighbors
    "KNN": KNeighborsRegressor(),

    # Kernel Methods
    "KernelRidge": KernelRidge(),

    # Gaussian Process
    "GaussianProcess": GaussianProcessRegressor(),

    # Industry Boosting Libraries
    "XGBoost": XGBRegressor(random_state=42, verbosity=0),
    "LightGBM": LGBMRegressor(random_state=42),
    "CatBoost": CatBoostRegressor(verbose=0, random_state=42)
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


# Convert results list into dictionary
all_models_performance = {name: float(rmse) for name, rmse in results}

metadata = {
    "model_name": best_name,
    "rmse": float(best_rmse),
    "trained_at": str(pd.Timestamp.now()),
    "version": version,
    "all_models_performance": all_models_performance
}

with open(metadata_path, "w") as f:

    json.dump(metadata, f)


print("================================")

print("Best model:", best_name)

print("RMSE:", best_rmse)

print("Model version saved:", version)

print("================================")