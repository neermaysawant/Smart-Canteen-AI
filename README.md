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

## Model Version History & Post-Mortem Analysis

This table documents the champion model elected at each retraining cycle, the dataset size at that point, and the RMSE. This is the **post-mortem record** — it shows how the system improved as more real data was collected.

| Version | Champion Model   | RMSE    | Records Used | Notes                                                     |
|---------|-----------------|---------|--------------|-----------------------------------------------------------|
| v1      | CatBoost        | 27.68   | ~400         | Initial synthetic dataset. CatBoost wins on categorical data natively. |
| v2      | CatBoost        | 27.43   | ~420         | Small data addition. CatBoost retains champion. Boosting still winning. |
| v3      | GradientBoosting| 26.89   | ~440         | More records; GradientBoosting edges out CatBoost as data distribution stabilises. |
| v4      | Lasso           | 26.34   | ~460         | Significant shift — linear model now competitive. Suggests the underlying data has a more linear structure than initially apparent. OHE features make Lasso very effective. |
| v5      | Lasso           | 26.02   | ~480         | Lasso retains champion. Linear regularisation proves stable as dataset grows. |

### Why did the champion shift from CatBoost to Lasso?

This is the most important question from a model lifecycle perspective. Two factors explain it:

1. **Data volume effect on linear models.** CatBoost's advantage is handling raw categorical features without preprocessing. Once OneHotEncoding is applied explicitly (as in this pipeline), that advantage disappears. With more data, Lasso's L1 regularisation can identify and zero out irrelevant OHE columns, giving it a precision edge over a complex ensemble on a relatively small dataset.

2. **The underlying signal is approximately linear.** Canteen demand is driven by a small number of strong signals (category, day, exam period) that interact additively. There is no deep nonlinear interaction that would justify the added variance of a boosted ensemble. As the dataset grew, the RMSE curve converged faster for Lasso than for CatBoost, confirming the linear hypothesis.

**Implication for future retraining:** if RMSE rises by more than 10% on the next cycle, the first suspect is data drift in menu composition — new items that Lasso's existing OHE vocabulary has not seen. At that point, retraining from scratch (rather than fine-tuning) is the right call.

---

## Features

### Operations Hub
The main working screen for canteen staff. Two panels side by side:

**Left — Demand Forecast**
Select the day, meal category, exam status, and build the menu using dropdowns that reflect the actual canteen menu structure (different options for Breakfast, Lunch, and each dinner type by day). Hit **Run Forecast** to get a predicted plate count with a % delta against the category average. After service, enter the actual plates served and commit it to the database. A progress bar shows how close you are to the next retrain threshold.

**Right — Live Analytics**
Nine interactive charts that update in real time as the database grows:
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
The technical view. Shows every model evaluated in the last training run with a ranked leaderboard, RMSE scores, performance gap vs the best model, and a normalised 0–100 score. Includes a radar chart for the top 8, a scatter plot of RMSE vs score, and a one-click retrain button that runs the full training pipeline and saves a new versioned model.

---

## Models

22 models are trained and evaluated on every run. The best performer is automatically selected and saved.

| Tier | Models |
|------|--------|
| Linear | LinearRegression, Ridge, **Lasso** ← current champion, ElasticNet, BayesianRidge, HuberRegressor, SGDRegressor, PassiveAggressiveRegressor |
| Tree | DecisionTreeRegressor |
| Ensemble | RandomForest, ExtraTrees, GradientBoosting, HistGradientBoosting, AdaBoost |
| Support Vector | SVR, LinearSVR |
| Neighbors | KNeighborsRegressor |
| Kernel | KernelRidge |
| Gaussian | GaussianProcessRegressor |
| Boosting | XGBoost, LightGBM, CatBoost |

**Current best:** Lasso · RMSE 26.02 · v5

Features used: `day_of_week`, `category`, `menu_item`, `is_exam_period`
Target: `plates_consumed`
Preprocessing: OneHotEncoder on categorical columns via sklearn Pipeline
Evaluation: 80/20 train-test split, RMSE

**Why RMSE over MAE?** RMSE penalises large errors more heavily. A 40-plate prediction error is operationally far worse than two 20-plate errors — running out of food mid-service is not equivalent to being off by a small margin consistently. RMSE's squaring term makes it the right loss metric for this domain.

**Why OneHotEncoder over LabelEncoder?** LabelEncoder assigns integers to categories (e.g. Monday=0, Friday=4), implying a false ordinal relationship. A linear model would then interpret Friday as "more than Monday" in some direction, which is meaningless. OHE gives each category its own binary feature column, which is semantically correct.

---

## Dataset

Synthetically generated to simulate an Indian university canteen. ~480 records, growing as staff log actual consumption.

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
Exam period reduces demand by ~15 plates with added noise (±25).

All data lives in `database/canteen.db` (SQLite).

---

## Pipeline Robustness & Data Drift Handling

### How new data flows through the system

```
Staff enters actual plates via dashboard
           │
           ▼
    INSERT into canteen_data (SQLite)
           │
           ▼
    st.cache_data cleared immediately
           │
           ▼
    Update counter increments (total % 42)
           │
    every 42 new records
           ▼
  ┌─────────────────────┐
  │   RETRAIN TRIGGER   │
  └──────────┬──────────┘
             │ subprocess.run(["python", train_models.py])
             ▼
    All 22 models retrained on full DB
             │
             ▼
    Best model saved as model_v{n}.pkl
    Champion history written to metadata
             │
             ▼
    Dashboard auto-loads latest .pkl
    (glob sorted by version number)
```

### Why 42 records?
42 is approximately 2 weeks of 3 daily meal services. It is large enough that the new data represents a meaningful shift in the distribution (not just noise), but small enough to trigger retraining before the model drifts significantly from the true distribution.

### Handling unseen menu items
`handle_unknown="ignore"` in the OneHotEncoder ensures that new menu items introduced after training do not crash the prediction pipeline — they are silently treated as an all-zero OHE row and the model falls back to predicting based on day, category, and exam period signals alone.

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
│   ├── model_v1_metadata.json  ← RMSE, timestamp, record count, champion history
│   ├── model_v2.pkl  ···  model_v5.pkl
│   └── model_v2_metadata.json  ···  model_v5_metadata.json
│
├── scripts/
│   ├── create_database.py      ← Creates the SQLite schema
│   ├── generate_data.py        ← Synthesizes and inserts records (supports --records and --seed flags)
│   ├── train_models.py         ← Trains all 22 models, saves best + full metadata with champion history
│   └── predict.py              ← Standalone CLI prediction script (supports --day, --category, --menu, --exam)
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

# 2. Generate synthetic training data (default 21 records; use --records N for more)
python scripts/generate_data.py --records 400

# 3. Train all models and save the best one
python scripts/train_models.py

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

**Running a standalone prediction**

```bash
# Uses the latest model automatically
python scripts/predict.py --day Friday --category Dinner --menu "Egg Curry + Palak Paneer" --exam 0

# With a specific model version
python scripts/predict.py --version 3 --day Monday --category Lunch --menu "Chana Masala + Bhindi Fry + Jeera Rice + Dal Tadka + Roti + Lassi"
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
  Champion history appended to metadata
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
| Semester start | Refresh synthetic data weights if menu changes; update OHE vocabulary |
| Annually | Audit feature relevance; consider adding weather, events, or holiday data |

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