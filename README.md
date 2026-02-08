# 🍽️ Smart Canteen AI — Demand Prediction System

## 📌 Project Overview

Smart Canteen AI is a production-style machine learning deployment project designed to predict food demand in a university canteen environment.

The system transforms traditional notebook-based ML workflows into a fully engineered application including:

- SQL-based data storage
- Automated model training pipeline
- Versioned model lifecycle
- Interactive prediction dashboard
- Real-time analytics visualization
- Human feedback loop for continuous improvement

The focus of this project is not only model performance but also usability, deployment engineering, and lifecycle maintenance.

---

## 🎯 Problem Statement

University canteens frequently face challenges such as:

- Over-preparation leading to food waste
- Under-preparation causing shortages
- Lack of data-driven decision-making

This project predicts the number of plates consumed based on:

- Day of the week
- Meal category (Breakfast / Lunch / Dinner)
- Menu composition
- Exam period indicator

The goal is to assist canteen staff in planning resources efficiently using predictive analytics.

---

## 📊 Dataset

The dataset is synthetically generated to simulate real-world Indian university canteen operations.

### Menu Structure

#### Breakfast
- Single-item meal.

#### Lunch
- 1 dry vegetable
- 1 gravy vegetable
- Rice
- Dal
- Indian bread
- Beverage

#### Dinner
- Monday/Tuesday/Thursday/Saturday: Veg gravy + rice + dal + bread
- Wednesday/Sunday: Chicken gravy + paneer gravy + rice + dal + bread
- Friday: Egg gravy + paneer gravy + rice + dal + bread

Data is stored in:

database/canteen.db

---

## 🤖 Model Implementation

Traditional ML models were used:

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

### Pipeline Steps

1. Load data from SQL database.
2. Encode categorical variables using OneHotEncoder.
3. Train multiple models.
4. Evaluate using RMSE.
5. Automatically select best-performing model.
6. Save trained model with versioning.

---

## 🔁 Model Versioning and Lifecycle

Every retraining creates a new version:

models/model_v1.pkl  
models/model_v2.pkl  
models/model_v3.pkl  

Each model includes metadata:

- Model name
- RMSE score
- Training timestamp
- Version number

The dashboard automatically loads the latest model.

---

## 🖥️ Dashboard Features

Built using Streamlit.

### 🔮 Prediction Page

- Dynamic menu selection UI
- Demand prediction using trained model
- Actual plates input
- Database update functionality
- Retraining alert after threshold updates

### 📊 Analytics Dashboard

- KPI Cards:
  - Total records
  - Average demand
  - Peak demand
- Interactive charts:
  - Demand by category
  - Weekly trends

### 🤖 Model Info

- Model version
- RMSE score
- Training timestamp
- One-click model retraining

---

## 🔁 Model Maintenance Workflow

1. User predicts demand.
2. Actual consumption entered after service.
3. Data saved into SQL database.
4. Update counter increases.
5. System indicates when retraining is required.
6. Retraining generates new model version.

---

## 📁 Project Structure

canteen_project/

dashboard/
    app.py

database/
    canteen.db

models/
    model_v1.pkl
    model_v1_metadata.json

scripts/
    train_model.py
    generate_data.py

README.md

---

## ⚙️ Installation

Install dependencies:

pip install streamlit pandas scikit-learn plotly

---

## ▶️ Run Dashboard

streamlit run dashboard/app.py

---

## 🔄 Retraining

Retraining can be triggered directly from the dashboard using:

🚀 Retrain Model

This creates a new versioned model automatically.

---

## 🚀 Engineering Highlights

- SQL-based data pipeline
- Model versioning
- Automated lifecycle workflow
- Interactive UI
- Analytics dashboard
- Production-style ML deployment

---

## 👨‍💻 Author

Developed as part of Hackathon 3 focusing on machine learning deployment and lifecycle engineering.