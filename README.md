# 🍽️ Smart Canteen AI – Demand Prediction System

## 📌 Overview

Smart Canteen AI is a machine learning-powered system designed to predict food demand in a university canteen environment. The goal of this project is to transform a traditional ML model into a usable, maintainable, and production-ready application.

Instead of existing only in notebooks, the trained model is integrated into a fully interactive dashboard where users can:

- Select daily menu configurations
- Predict expected food consumption
- Record actual consumption data
- Maintain a lifecycle-aware ML system with retraining indicators

This project demonstrates real-world ML engineering principles including data pipelines, model deployment, UI interaction, and lifecycle management.

---

## 🎯 Problem Statement

University canteens often struggle with:

- Food wastage due to over-preparation
- Food shortages due to underestimation
- Lack of data-driven planning

This system predicts the number of plates consumed based on:

- Day of the week
- Meal category (Breakfast / Lunch / Dinner)
- Menu composition
- Exam period indicator

The aim is to support smarter planning and resource optimization.

---

## 📊 Dataset

The dataset is synthetically generated using realistic Indian university canteen logic.

### Menu Structure

#### Breakfast
- Single-item meal selection.

#### Lunch
- 1 gravy vegetable
- 1 dry vegetable
- Rice
- Dal
- Indian bread
- Beverage

#### Dinner
- Veg days: 1 gravy veg + rice + dal + bread
- Wednesday & Sunday: Chicken gravy + Paneer gravy + rice + dal + bread
- Friday: Egg gravy + Paneer gravy + rice + dal + bread

Additional randomness is introduced to simulate realistic variation.

Data is stored in an SQLite database:

database/canteen.db

---

## 🤖 Model Implementation

Traditional ML models were used (Neural Networks excluded as per requirement):

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor

### Pipeline Steps

1. Load data from SQL database.
2. Feature encoding using OneHotEncoder.
3. Train multiple models.
4. Evaluate using RMSE.
5. Select best-performing model automatically.
6. Serialize trained pipeline.

Saved files:

models/model_v1.pkl  
models/model_v1_metadata.json

---

## 🖥️ Dashboard

The Streamlit dashboard provides:

- Interactive menu selection UI.
- Dynamic input fields based on meal category.
- Real-time demand prediction.
- Model information panel showing:
  - Model name
  - RMSE score
  - Training timestamp

### User Workflow

1. Select day and category.
2. Configure menu using dropdowns.
3. Predict required plates.
4. Enter actual plates consumed.
5. Update database with new observations.

---

## 🔁 Model Lifecycle Management

The system tracks updates to the dataset.

Every new actual data entry:

- Is saved into the SQL database.
- Increments update count.
- Displays retraining indicator.

After 90 updates:

🚨 Model retraining required.

This simulates a production ML lifecycle process.

---

## 📁 Project Structure

project_root/

dashboard/
  app.py

database/
  canteen.db

models/
  model_v1.pkl
  model_v1_metadata.json

scripts/
  generate_data.py
  train_model.py

README.md

---

## ⚙️ Installation

Install dependencies:

pip install streamlit pandas scikit-learn

---

## ▶️ Run Dashboard

streamlit run dashboard/app.py

---

## 📈 Future Improvements

- Automatic retraining from dashboard
- Model version history tracking
- Live analytics charts
- Multi-model comparison UI

---

## 👨‍💻 Author

Developed as part of Hackathon 3 focusing on ML deployment and lifecycle engineering.