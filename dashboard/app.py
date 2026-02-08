import streamlit as st
import os
import pickle
import pandas as pd
import json
import sqlite3
import plotly.express as px
import subprocess
import glob

# Page setup
st.set_page_config(page_title="Smart Canteen AI", layout="wide")


# Load Latest Model Automatically

base_dir = os.path.dirname(os.path.dirname(__file__))
models_dir = os.path.join(base_dir, 'models')
db_path = os.path.join(base_dir, 'database', 'canteen.db')

model_files = sorted(glob.glob(os.path.join(models_dir, "model_v*.pkl")))
latest_model = model_files[-1]
metadata_path = latest_model.replace(".pkl", "_metadata.json")

with open(latest_model, "rb") as f:
    model = pickle.load(f)

with open(metadata_path, "r") as f:
    metadata = json.load(f)


# Session state

if "prediction_made" not in st.session_state:
    st.session_state.prediction_made = False


# Title
st.title("🍽️ Smart Canteen AI - Demand Prediction System")


# Sidebar Navigation

page = st.sidebar.radio(
    "Navigation",
    ["🔮 Prediction", "📊 Analytics Dashboard", "🤖 Model Info"]
)


# MENU

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

breakfast_items = ["Idli","Medu Vada","Poha","Upma","Masala Dosa","Plain Dosa","Aloo Paratha","Paneer Paratha"]

dry_veg = ["Bhindi Fry","Aloo Gobi","Beans Poriyal","Cabbage Sabzi"]
gravy_veg = ["Mixed Veg Curry","Chana Masala","Veg Kofta","Malai Kofta"]
rice_items = ["Jeera Rice","Plain Rice","Veg Pulao"]
dal_items = ["Dal Tadka","Sambar","Dal Fry"]
indian_bread = ["Roti","Chapati","Naan"]
beverages = ["Curd","Lassi","Buttermilk"]

paneer_gravies = ["Paneer Butter Masala","Shahi Paneer","Kadai Paneer"]
chicken_gravies = ["Chicken Curry","Butter Chicken","Chicken Kadai"]
egg_gravies = ["Egg Curry","Anda Masala","Egg Korma"]


# Model Info Page

if page == "🤖 Model Info":

    st.subheader("📊 Model Information")

    col1, col2, col3 = st.columns(3)
    col1.metric("Model Used", metadata["model_name"])
    col2.metric("RMSE", round(metadata["rmse"], 2))
    col3.metric("Version", metadata["version"])

    st.markdown("---")

    # Retrain Button

    if st.button("🚀 Retrain Model"):

        with st.spinner("Retraining model..."):

            train_script = os.path.join(base_dir, "scripts", "train_models.py")

            result = subprocess.run(
                ["python", train_script],
                capture_output=True,
                text=True
            )

            print(result.stdout)
            print(result.stderr)

        st.success("Model retrained successfully!")

        # Force full app reload
        st.rerun()



# Prediction Page

if page == "🔮 Prediction":

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


    st.success(f"Selected Menu: {menu_item}")

    predict_clicked = st.button("🔮 Predict Demand")

    if predict_clicked:
        st.session_state.prediction_made = True


    if st.session_state.prediction_made:

        input_data = pd.DataFrame([{
            "day_of_week": day,
            "category": category,
            "menu_item": menu_item,
            "is_exam_period": exam_period
        }])

        prediction = model.predict(input_data)

        st.metric("Predicted Plates", int(prediction[0]))

        actual_plates = st.number_input("Enter Actual Plates Consumed", min_value=0)

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
                st.error("🚨 Model retraining required now!")
            else:
                st.info(f"Updates since last retrain: {total_rows % 90}/90")


# Analytics Page

if page == "📊 Analytics Dashboard":

    st.subheader("📊 Canteen Analytics")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM canteen_data", conn)
    conn.close()

    k1,k2,k3 = st.columns(3)
    k1.metric("Total Records", len(df))
    k2.metric("Average Plates", int(df["plates_consumed"].mean()))
    k3.metric("Peak Demand", int(df["plates_consumed"].max()))

    fig1 = px.bar(df.groupby("category", as_index=False)["plates_consumed"].mean(),
                  x="category", y="plates_consumed", color="category",
                  title="Demand by Category")

    st.plotly_chart(fig1, use_container_width=True)