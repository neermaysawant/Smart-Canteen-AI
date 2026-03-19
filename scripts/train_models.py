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


# ── Paths ──────────────────────────────────────────────────────────────────────

base_dir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database', 'canteen.db')
models_dir = os.path.join(base_dir, 'models')
os.makedirs(models_dir, exist_ok=True)


# ── Load Data ──────────────────────────────────────────────────────────────────

conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM canteen_data", conn)
conn.close()

if df.empty:
    raise ValueError("Database has no data. Run generate_data.py first.")

print(f"Data loaded: {df.shape[0]} records, {df.shape[1]} columns")
print(f"  Category breakdown: {df['category'].value_counts().to_dict()}")
print(f"  Exam period records: {df['is_exam_period'].sum()} / {len(df)}")
print(f"  Target range: {df['plates_consumed'].min()} – {df['plates_consumed'].max()} plates")


# ── Features and Target ────────────────────────────────────────────────────────

X = df[["day_of_week", "category", "menu_item", "is_exam_period"]]
y = df["plates_consumed"]

categorical_features = ["day_of_week", "category", "menu_item"]


# ── Preprocessing Pipeline ─────────────────────────────────────────────────────
# OneHotEncoder chosen over LabelEncoder because our tree-based and linear
# models both benefit from explicit binary columns — label encoding would
# imply a false ordinal relationship between categories like "Monday" < "Friday".
# handle_unknown="ignore" ensures unseen menu items at inference don't crash.

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
    ],
    remainder="passthrough"   # passes is_exam_period through unchanged
)


# ── Model Registry ─────────────────────────────────────────────────────────────

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


# ── Train / Test Split ─────────────────────────────────────────────────────────
# 80/20 split gives enough training data for OHE to see all menu combinations
# while reserving a meaningful holdout for RMSE evaluation.

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}")
print("─" * 48)


# ── Train All Models ───────────────────────────────────────────────────────────

best_model = None
best_rmse = float("inf")
best_name = ""
results = []

for name, model in models.items():

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    # RMSE used (not MAE) because it penalises large over/under-preparation
    # errors more heavily — a 40-plate error is far worse than two 20-plate errors
    # for canteen operations (wasted food vs. running out mid-service).
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5

    print(f"{name:<30} RMSE: {rmse:.4f}")
    results.append((name, rmse))

    if rmse < best_rmse:
        best_rmse = rmse
        best_model = pipeline
        best_name = name


# ── Version Detection ──────────────────────────────────────────────────────────

existing_models = [
    f for f in os.listdir(models_dir)
    if f.startswith("model_v") and f.endswith(".pkl")
]
version = len(existing_models) + 1

model_path = os.path.join(models_dir, f"model_v{version}.pkl")
metadata_path = os.path.join(models_dir, f"model_v{version}_metadata.json")


# ── Load Champion History for post-mortem tracking ────────────────────────────
# Reads all previous metadata files to build a version-by-version champion log.
# This powers the post-mortem analysis in the dashboard.

champion_history = []
for v in range(1, version):
    prev_meta = os.path.join(models_dir, f"model_v{v}_metadata.json")
    if os.path.exists(prev_meta):
        with open(prev_meta, "r") as f:
            prev = json.load(f)
        champion_history.append({
            "version": v,
            "champion": prev.get("model_name", "unknown"),
            "rmse": prev.get("rmse", None),
            "trained_at": prev.get("trained_at", ""),
            "record_count": prev.get("record_count", None)
        })


# ── Save Best Model ────────────────────────────────────────────────────────────

with open(model_path, "wb") as f:
    pickle.dump(best_model, f)

all_models_performance = {name: float(rmse) for name, rmse in results}

metadata = {
    "model_name": best_name,
    "rmse": float(best_rmse),
    "trained_at": str(pd.Timestamp.now()),
    "version": version,
    "record_count": len(df),
    "train_size": len(X_train),
    "test_size": len(X_test),
    "features": ["day_of_week", "category", "menu_item", "is_exam_period"],
    "target": "plates_consumed",
    "champion_history": champion_history,
    "all_models_performance": all_models_performance
}

with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)


# ── Summary ────────────────────────────────────────────────────────────────────

print("\n" + "=" * 48)
print(f"  Champion model : {best_name}")
print(f"  RMSE           : {best_rmse:.4f}")
print(f"  Version saved  : v{version}")
print(f"  Records used   : {len(df)}")
if champion_history:
    prev_rmse = champion_history[-1]["rmse"]
    prev_champ = champion_history[-1]["champion"]
    delta = prev_rmse - best_rmse if prev_rmse else 0
    direction = "improved" if delta > 0 else "degraded"
    print(f"  vs v{version-1}          : {prev_champ} RMSE {prev_rmse:.4f} → {direction} by {abs(delta):.4f}")
print("=" * 48)