import os
import pickle
import pandas as pd

# paths
base_dir = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(base_dir, 'models', 'model_v1.pkl')

# load trained pipeline
with open(model_path, "rb") as f:
    model = pickle.load(f)

print("Model loaded successfully!")

# example input (you can change values)
new_data = pd.DataFrame([{
    "day_of_week": "Wednesday",
    "category": "Dinner",
    "menu_item": "Chicken Curry + Paneer Butter Masala",
    "is_exam_period": 0
}])

prediction = model.predict(new_data)

print("Predicted plates:", int(prediction[0]))