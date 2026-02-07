import streamlit as st
import os
import pickle
import pandas as pd
import json
import sqlite3


# Page setup
st.set_page_config(page_title="Smart Canteen AI", layout="wide")

# Session state for prediction persistence
if "prediction_made" not in st.session_state:
    st.session_state.prediction_made = False

# Load Model

base_dir = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(base_dir, 'models', 'model_v1.pkl')
metadata_path = os.path.join(base_dir, 'models', 'model_v1_metadata.json')
db_path = os.path.join(base_dir, 'database', 'canteen.db')

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(metadata_path, "r") as f:
    metadata = json.load(f)

# Title
st.title("🍽️ Smart Canteen AI - Demand Prediction")

# Model Info
st.subheader("📊 Model Information")

col1, col2, col3 = st.columns(3)
col1.metric("Model Used", metadata["model_name"])
col2.metric("RMSE", round(metadata["rmse"], 2))
col3.metric("Last Trained", metadata["trained_at"])

st.markdown("---")

# MENU

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

breakfast_items = ["Idli","Medu Vada","Poha","Upma","Masala Dosa","Plain Dosa","Aloo Paratha","Paneer Paratha","Vegetable Sandwich","Pav Bhaji","Sabudana Khichdi","Sheera","Uttapam"]

dry_veg = ["Bhindi Fry","Aloo Gobi","Beans Poriyal","Cabbage Sabzi","Aloo Methi","Tinda Masala","Gajar Matar","Baingan Bharta Dry","Karela Fry"]
gravy_veg = ["Mixed Veg Curry","Chana Masala","Veg Kofta","Malai Kofta","Rajma Masala","Kadhi Pakoda","Aloo Dum","Mushroom Masala","Navratan Korma","Vegetable Kurma"]
rice_items = ["Jeera Rice","Plain Rice","Veg Pulao","Peas Pulao","Lemon Rice","Curd Rice","Tomato Rice"]
dal_items = ["Dal Tadka","Sambar","Dal Fry","Moong Dal","Dal Makhani","Gujarati Dal"]
indian_bread = ["Roti","Chapati","Naan","Tandoori Roti","Phulka"]
beverages = ["Curd","Tang","Lemonade","Lassi","Buttermilk","Jaljeera","Rose Milk"]

paneer_gravies = ["Paneer Butter Masala","Shahi Paneer","Kadai Paneer","Palak Paneer","Matar Paneer","Paneer Lababdar","Paneer Do Pyaza","Paneer Tikka Masala"]
chicken_gravies = ["Chicken Curry","Butter Chicken","Chicken Masala","Chicken Do Pyaza","Chicken Kolhapuri","Chicken Handi","Chicken Kadai"]
egg_gravies = ["Egg Curry","Anda Masala","Egg Bhurji Gravy","Egg Korma","Masala Egg Curry"]

# User Inputs

st.subheader("🔮 Demand Prediction")

colA, colB, colC = st.columns(3)

with colA:
    day = st.selectbox("Select Day", days)

with colB:
    category = st.selectbox("Select Category", ["Breakfast","Lunch","Dinner"])

with colC:
    exam_choice = st.selectbox("Exam Period?", ["No", "Yes"])
    exam_period = 1 if exam_choice == "Yes" else 0

# BREAKFAST

if category == "Breakfast":
    menu_item = st.selectbox("Breakfast Item", breakfast_items)

# LUNCH

elif category == "Lunch":

    gravy = st.selectbox("Gravy Vegetable", gravy_veg)
    dry = st.selectbox("Dry Vegetable", dry_veg)
    rice = st.selectbox("Rice", rice_items)
    dal = st.selectbox("Dal", dal_items)
    bread = st.selectbox("Bread", indian_bread)
    beverage = st.selectbox("Beverage", beverages)

    menu_item = f"{gravy} + {dry} + {rice} + {dal} + {bread} + {beverage}"

# DINNER

elif category == "Dinner":

    if day in ["Monday","Tuesday","Thursday","Saturday"]:
        gravy = st.selectbox("Veg Gravy", gravy_veg)
        menu_item = gravy

    elif day in ["Wednesday","Sunday"]:
        chicken = st.selectbox("Chicken Gravy", chicken_gravies)
        paneer = st.selectbox("Paneer Gravy", paneer_gravies)
        menu_item = f"{chicken} + {paneer}"

    elif day == "Friday":
        egg = st.selectbox("Egg Gravy", egg_gravies)
        paneer = st.selectbox("Paneer Gravy", paneer_gravies)
        menu_item = f"{egg} + {paneer}"

    rice = st.selectbox("Rice", rice_items)
    dal = st.selectbox("Dal", dal_items)
    bread = st.selectbox("Bread", indian_bread)

    menu_item += f" + {rice} + {dal} + {bread}"

# Menu preview
st.info(f"Selected Menu: {menu_item}")

# Predict Button

col_left, col_center, col_right = st.columns([1,2,1])

with col_center:
    predict_clicked = st.button("🔮 Predict Demand")

if predict_clicked:
    st.session_state.prediction_made = True

# Prediction block

if st.session_state.prediction_made:

    input_data = pd.DataFrame([{
        "day_of_week": day,
        "category": category,
        "menu_item": menu_item,
        "is_exam_period": exam_period
    }])

    prediction = model.predict(input_data)

    st.markdown("### 🍽️ Estimated Plates Required")
    st.metric(label="Predicted Plates", value=int(prediction[0]))

    st.markdown("---")

    actual_plates = st.number_input(
        "Enter Actual Plates Consumed (after service)",
        min_value=0,
        step=1
    )

    update_clicked = st.button("✅ Update Database")

    if update_clicked:

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO canteen_data(
                day_of_week,
                category,
                menu_item,
                is_exam_period,
                plates_consumed
            ) VALUES (?, ?, ?, ?, ?)
        """, (day, category, menu_item, exam_period, actual_plates))

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM canteen_data")
        total_rows = cursor.fetchone()[0]

        conn.close()

        st.success("Database updated successfully!")

        updates_since_retrain = total_rows % 90

        if updates_since_retrain == 0:
            st.error("🚨 Model retraining required now! Please retrain the model.")
        else:
            st.info(f"🔁 Updates since last retrain: {updates_since_retrain} / 90")