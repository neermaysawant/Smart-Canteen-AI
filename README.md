# CANTEENIQ · Intelligence Platform
### University Canteen · Demand Forecasting System

---

```
  ██████╗ █████╗ ███╗   ██╗████████╗███████╗███████╗███╗   ██╗██╗ ██████╗
 ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔════╝██╔════╝████╗  ██║██║██╔═══██╗
 ██║     ███████║██╔██╗ ██║   ██║   █████╗  █████╗  ██╔██╗ ██║██║██║   ██║
 ██║     ██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══╝  ██║╚██╗██║██║██║▄▄ ██║
 ╚██████╗██║  ██║██║ ╚████║   ██║   ███████╗███████╗██║ ╚████║██║╚██████╔╝
  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝ ╚══▀▀═╝
```

> **Production-style ML deployment** · 22 models evaluated · Auto-versioned · Live feedback loop

---

## What is this?

CanteenIQ is a machine learning deployment project built for a university canteen environment. It solves a real operational problem — canteen staff have no reliable way to know how much food to prepare each day, leading to waste when they overprepare and shortages when they underprepare.

The system predicts the number of plates that will be consumed for any given meal service, based on the day of the week, meal category, menu composition, and whether it's an exam period. Staff can enter the actual plates served after each meal, which feeds back into the model's training data. When enough new data accumulates, the model retrains automatically into a new versioned file.

The focus here is not just on model accuracy — it's on the full deployment lifecycle: data storage, training pipelines, versioning, a usable interface, and a maintenance plan.

---

## The Problem

University canteens consistently face three pain points:

- **Overpreparation** → food waste, higher costs
- **Underpreparation** → student dissatisfaction, shortages
- **No feedback mechanism** → decisions made on gut feel, not data

CanteenIQ addresses all three by turning historical consumption data into forward-looking predictions, and by continuously improving those predictions as more real-world data is collected.

---

## Features

### Operations Hub
The main working screen for canteen staff. Two panels side by side:

**Left — Demand Forecast**
Select the day, meal category, exam status, and build the menu using dropdowns that reflect the actual canteen menu structure (different options for Breakfast, Lunch, and each dinner type by day). Hit **Run Forecast** to get a predicted plate count with a % delta against the category average. After service, enter the actual plates served and commit it to the database. A progress bar shows how close you are to the next retrain threshold.

**Right — Live Analytics**
Eight interactive charts that update in real time as the database grows:
- Weekly demand radar (normal vs exam overlay)
- Stacked area chart by category across days
- Utilisation vs peak capacity bullet bars
- Violin distribution per meal category
- Weekly volume waterfall
- Sankey flow diagram (Day → Category → Volume tier)
- Menu demand treemap (top 20 items)
- Rolling average sparklines per category
- Strip plot of individual records with exam/normal split

### Model Intelligence
The technical view. Shows every model that was evaluated in the last training run with a ranked leaderboard, RMSE scores, performance gap vs the best model, and a normalised 0–100 score. Includes a radar chart for the top 8, a scatter plot of RMSE vs score, and a one-click retrain button that runs the full training pipeline and saves a new versioned model.

---

## Models

22 models are trained and evaluated on every run. The best performer is automatically selected and saved.

| Tier | Models |
|------|--------|
| Linear | LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge, HuberRegressor, SGDRegressor, PassiveAggressiveRegressor |
| Tree | DecisionTreeRegressor |
| Ensemble | RandomForest, ExtraTrees, GradientBoosting, HistGradientBoosting, AdaBoost |
| Support Vector | SVR, LinearSVR |
| Neighbors | KNeighborsRegressor |
| Kernel | KernelRidge |
| Gaussian | GaussianProcessRegressor |
| Boosting | XGBoost, LightGBM, **CatBoost** ← current champion |

**Current best:** CatBoost · RMSE 27.43 · v2

Features used: `day_of_week`, `category`, `menu_item`, `is_exam_period`
Target: `plates_consumed`
Preprocessing: OneHotEncoder on categorical columns via sklearn Pipeline
Evaluation: 80/20 train-test split, RMSE

---

## Dataset

Synthetically generated to simulate an Indian university canteen. 400 base records, growing as staff log actual consumption.

**Menu structure:**

```
Breakfast   →  Single item (Idli, Dosa, Paratha, etc.)

Lunch       →  Gravy veg + Dry veg + Rice + Dal + Bread + Beverage

Dinner
  Mon/Tue/Thu/Sat  →  Veg gravy + Rice + Dal + Bread
  Wed/Sun          →  Chicken gravy + Paneer gravy + Rice + Dal + Bread
  Fri              →  Egg gravy + Paneer gravy + Rice + Dal + Bread
  (~33% chance)    →  + Sweet dish
```

Demand ranges: Breakfast 60–120 · Lunch 120–200 · Dinner 100–180
Exam period reduces demand by ~15 plates with added noise.

All data lives in `database/canteen.db` (SQLite).

---

## Project Structure

```
canteen_project/
│
├── dashboard/
│   └── app.py                  ← Streamlit dashboard (Operations Hub + Model Intelligence)
│
├── database/
│   └── canteen.db              ← SQLite database (auto-created, not in repo)
│
├── models/
│   ├── model_v1.pkl            ← Trained pipeline (versioned)
│   ├── model_v1_metadata.json  ← RMSE, timestamp, all model scores
│   ├── model_v2.pkl
│   └── model_v2_metadata.json
│
├── scripts/
│   ├── create_database.py      ← Creates the SQLite schema
│   ├── generate_data.py        ← Synthesizes and inserts 400 records
│   ├── train_models.py         ← Trains all 22 models, saves best + metadata
│   └── predict.py              ← Standalone prediction script (CLI)
│
└── README.md
```

> **Note:** `database/canteen.db` and `models/*.pkl` are excluded from the repository. Run the setup steps below to regenerate them locally.

---

## Setup

**Requirements**

```bash
pip install streamlit pandas scikit-learn plotly xgboost lightgbm catboost
```

**First-time setup** (run in order)

```bash
# 1. Create the database schema
python scripts/create_database.py

# 2. Generate synthetic training data
python scripts/generate_data.py

# 3. Train all models and save the best one
python scripts/train_models.py

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

---

## Model Lifecycle

```
Staff logs prediction + actual
           │
           ▼
    Database updated
           │
           ▼
   Update counter +1
           │
    every 42 updates
           ▼
  ┌─────────────────┐
  │  RETRAIN ALERT  │
  └────────┬────────┘
           │
           ▼
  Run train_models.py
  (or click Retrain in dashboard)
           │
           ▼
  New model_v{n}.pkl saved
  Dashboard auto-loads latest
```

The 42-update threshold is configurable in `app.py`. Each retrain evaluates all 22 models fresh and promotes the new best performer.

---

## Maintenance Timeline

| Frequency | Action |
|-----------|--------|
| Every service | Log actual plates consumed via dashboard |
| Every 42 new records | Trigger model retrain |
| Monthly | Review model RMSE trend; investigate drift if RMSE rises >10% |
| Semester start | Refresh synthetic data weights if menu changes |
| Annually | Audit feature relevance; consider adding weather, events data |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Dashboard | Streamlit |
| Visualisation | Plotly (go, px) |
| ML | scikit-learn, XGBoost, LightGBM, CatBoost |
| Data | SQLite via Python sqlite3 |
| Serialisation | pickle + JSON metadata |
| Language | Python 3.10+ |

---

## Author

**Neermay Sawant**

Developed as part of **Hackathon 3** · Machine Learning Deployment & Lifecycle Engineering