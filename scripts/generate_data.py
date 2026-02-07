import sqlite3
import os
import random

# Database Connection

base_dir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database', 'canteen.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# Menu Components


days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# Breakfast options (1 item only)
breakfast_items = ["Idli","Medu Vada","Poha","Upma","Masala Dosa","Plain Dosa","Aloo Paratha","Paneer Paratha","Vegetable Sandwich","Pav Bhaji","Sabudana Khichdi","Sheera","Uttapam"]

# Lunch components (always same structure)
dry_veg = ["Bhindi Fry","Aloo Gobi","Beans Poriyal","Cabbage Sabzi","Aloo Methi","Tinda Masala","Gajar Matar","Baingan Bharta Dry","Karela Fry"]
gravy_veg = ["Mixed Veg Curry","Chana Masala","Veg Kofta","Malai Kofta","Rajma Masala","Kadhi Pakoda","Aloo Dum","Mushroom Masala","Navratan Korma","Vegetable Kurma"]
rice_items = ["Jeera Rice","Plain Rice","Veg Pulao","Peas Pulao","Lemon Rice","Curd Rice","Tomato Rice"]
dal_items = ["Dal Tadka","Sambar","Dal Fry","Moong Dal","Dal Makhani","Gujarati Dal"]
indian_bread = ["Roti","Chapati","Naan","Tandoori Roti","Phulka"]
beverages = ["Curd","Tang","Lemonade","Lassi","Buttermilk","Jaljeera","Rose Milk"]

# Paneer gravies
paneer_gravies = ["Paneer Butter Masala","Shahi Paneer","Kadai Paneer","Palak Paneer","Matar Paneer","Paneer Lababdar","Paneer Do Pyaza","Paneer Tikka Masala"]

# Chicken gravies (Wed & Sun)
chicken_gravies = ["Chicken Curry","Butter Chicken","Chicken Masala","Chicken Do Pyaza","Chicken Kolhapuri","Chicken Handi","Chicken Kadai"]

# Egg gravies (Friday)
egg_gravies = ["Egg Curry","Anda Masala","Egg Bhurji Gravy","Egg Korma","Masala Egg Curry"]

# sweets (3 times/week approx)
sweets = ["Gulab Jamun","Kheer","Halwa","Rasmalai","Jalebi","Sheera","Rice Kheer","Moong Dal Halwa"]

# Genetrating Fucntions

def generate_breakfast():
    menu_item = random.choice(breakfast_items)
    demand = random.randint(60,120)
    return menu_item, demand


def generate_lunch():

    dry = random.choice(dry_veg)
    gravy = random.choice(gravy_veg)

    rice = random.choice(rice_items)
    dal = random.choice(dal_items)
    bread = random.choice(indian_bread)
    beverage = random.choice(beverages)

    # primary menu identifier
    menu_item = f"{gravy} + {dry} + {rice} + {dal} + {bread} + {beverage}"

    demand = random.randint(120,200)

    return menu_item, demand


def generate_dinner(day):

    # Monday, Tuesday, Thursday, Saturday -> veg gravy
    if day in ["Monday","Tuesday","Thursday","Saturday"]:
        menu_item = random.choice(gravy_veg)

    # Wednesday & Sunday -> chicken + paneer option
    elif day in ["Wednesday","Sunday"]:
        menu_item = f"{random.choice(chicken_gravies)} + {random.choice(paneer_gravies)}"

    # Friday -> egg + paneer option
    elif day == "Friday":
        menu_item = f"{random.choice(egg_gravies)} + {random.choice(paneer_gravies)}"

    # Sweet approx 3 times/week
    include_sweet = random.choice([True, False, False])

    if include_sweet:
        menu_item += f" + {random.choice(sweets)}"

    rice = random.choice(rice_items)
    dal = random.choice(dal_items)
    bread = random.choice(indian_bread)

    menu_item += f" + {rice} + {dal} + {bread}"

    demand = random.randint(100,180)

    return menu_item, demand


# Data Generation

records_to_generate = 400

for i in range(records_to_generate):

    day = random.choice(days)
    category = random.choice(["Breakfast","Lunch","Dinner"])
    exam_period = random.choice([0,1])

    if category == "Breakfast":
        menu_item, base_demand = generate_breakfast()

    elif category == "Lunch":
        menu_item, base_demand = generate_lunch()

    else:
        menu_item, base_demand = generate_dinner(day)

    # exam period reduces demand slightly
    if exam_period == 1:
        base_demand -= 15

    plates_consumed = max(20, base_demand + random.randint(-25,25))

    cursor.execute("""
        INSERT INTO canteen_data(
            day_of_week,
            category,
            menu_item,
            is_exam_period,
            plates_consumed
        ) VALUES (?, ?, ?, ?, ?)
    """, (day, category, menu_item, exam_period, plates_consumed))

conn.commit()
conn.close()

print("Structured Indian canteen dataset generated successfully!")