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
