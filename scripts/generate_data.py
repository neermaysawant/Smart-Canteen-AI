import sqlite3
import os
import random
import argparse

# ── CLI Arguments ──────────────────────────────────────────────────────────────
# Allows running: python generate_data.py --records 50 --seed 99
# Default behaviour (no args) is unchanged: 21 records, random seed.

parser = argparse.ArgumentParser(description="Generate synthetic canteen data and insert into the database.")
parser.add_argument("--records", type=int, default=21, help="Number of records to generate (default: 21)")
parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility (default: random)")
args = parser.parse_args()

if args.seed is not None:
    random.seed(args.seed)


# ── Database Connection ────────────────────────────────────────────────────────

base_dir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database', 'canteen.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# ── Menu Components ────────────────────────────────────────────────────────────

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Breakfast: single item served
breakfast_items = [
    "Idli", "Medu Vada", "Poha", "Upma", "Masala Dosa", "Plain Dosa",
    "Aloo Paratha", "Paneer Paratha", "Vegetable Sandwich", "Pav Bhaji",
    "Sabudana Khichdi", "Sheera", "Uttapam"
]

# Lunch: full thali structure
dry_veg = [
    "Bhindi Fry", "Aloo Gobi", "Beans Poriyal", "Cabbage Sabzi",
    "Aloo Methi", "Tinda Masala", "Gajar Matar", "Baingan Bharta Dry", "Karela Fry"
]
gravy_veg = [
    "Mixed Veg Curry", "Chana Masala", "Veg Kofta", "Malai Kofta", "Rajma Masala",
    "Kadhi Pakoda", "Aloo Dum", "Mushroom Masala", "Navratan Korma", "Vegetable Kurma"
]
rice_items = ["Jeera Rice", "Plain Rice", "Veg Pulao", "Peas Pulao", "Lemon Rice", "Curd Rice", "Tomato Rice"]
dal_items  = ["Dal Tadka", "Sambar", "Dal Fry", "Moong Dal", "Dal Makhani", "Gujarati Dal"]
indian_bread = ["Roti", "Chapati", "Naan", "Tandoori Roti", "Phulka"]
beverages  = ["Curd", "Tang", "Lemonade", "Lassi", "Buttermilk", "Jaljeera", "Rose Milk"]

# Dinner proteins (day-dependent)
paneer_gravies  = [
    "Paneer Butter Masala", "Shahi Paneer", "Kadai Paneer", "Palak Paneer",
    "Matar Paneer", "Paneer Lababdar", "Paneer Do Pyaza", "Paneer Tikka Masala"
]
chicken_gravies = [
    "Chicken Curry", "Butter Chicken", "Chicken Masala", "Chicken Do Pyaza",
    "Chicken Kolhapuri", "Chicken Handi", "Chicken Kadai"
]
egg_gravies = ["Egg Curry", "Anda Masala", "Egg Bhurji Gravy", "Egg Korma", "Masala Egg Curry"]
sweets = [
    "Gulab Jamun", "Kheer", "Halwa", "Rasmalai", "Jalebi",
    "Sheera", "Rice Kheer", "Moong Dal Halwa"
]


# ── Generation Functions ───────────────────────────────────────────────────────

def generate_breakfast():
    """Single breakfast item. Demand: 60–120 plates."""
    menu_item = random.choice(breakfast_items)
    demand = random.randint(60, 120)
    return menu_item, demand


def generate_lunch():
    """Full thali: gravy + dry + rice + dal + bread + beverage. Demand: 120–200."""
    gravy    = random.choice(gravy_veg)
    dry      = random.choice(dry_veg)
    rice     = random.choice(rice_items)
    dal      = random.choice(dal_items)
    bread    = random.choice(indian_bread)
    beverage = random.choice(beverages)
    menu_item = f"{gravy} + {dry} + {rice} + {dal} + {bread} + {beverage}"
    demand = random.randint(120, 200)
    return menu_item, demand


def generate_dinner(day):
    """
    Dinner protein varies by day:
      Mon/Tue/Thu/Sat → veg gravy only
      Wed/Sun         → chicken + paneer
      Fri             → egg + paneer
    Sweet dish included ~33% of the time across all days.
    Demand: 100–180 plates.
    """
    if day in ["Monday", "Tuesday", "Thursday", "Saturday"]:
        menu_item = random.choice(gravy_veg)
    elif day in ["Wednesday", "Sunday"]:
        menu_item = f"{random.choice(chicken_gravies)} + {random.choice(paneer_gravies)}"
    elif day == "Friday":
        menu_item = f"{random.choice(egg_gravies)} + {random.choice(paneer_gravies)}"

    # Sweet dish ~33% of the time
    if random.choice([True, False, False]):
        menu_item += f" + {random.choice(sweets)}"

    rice  = random.choice(rice_items)
    dal   = random.choice(dal_items)
    bread = random.choice(indian_bread)
    menu_item += f" + {rice} + {dal} + {bread}"

    demand = random.randint(100, 180)
    return menu_item, demand


# ── Data Generation Loop ───────────────────────────────────────────────────────

records_to_generate = args.records
inserted = 0
category_counts = {"Breakfast": 0, "Lunch": 0, "Dinner": 0}

for _ in range(records_to_generate):

    day      = random.choice(days)
    category = random.choice(["Breakfast", "Lunch", "Dinner"])
    exam_period = random.choice([0, 1])

    if category == "Breakfast":
        menu_item, base_demand = generate_breakfast()
    elif category == "Lunch":
        menu_item, base_demand = generate_lunch()
    else:
        menu_item, base_demand = generate_dinner(day)

    # Exam period suppresses demand by ~15 plates (students study off-campus, skip meals)
    if exam_period == 1:
        base_demand -= 15

    # Add realistic noise: ±25 plates around the base demand
    plates_consumed = max(20, base_demand + random.randint(-25, 25))

    cursor.execute("""
        INSERT INTO canteen_data(
            day_of_week,
            category,
            menu_item,
            is_exam_period,
            plates_consumed
        ) VALUES (?, ?, ?, ?, ?)
    """, (day, category, menu_item, exam_period, plates_consumed))

    inserted += 1
    category_counts[category] += 1


conn.commit()
conn.close()


# ── Summary ────────────────────────────────────────────────────────────────────

print(f"Generated {inserted} records successfully.")
print(f"  Breakdown: Breakfast={category_counts['Breakfast']}  Lunch={category_counts['Lunch']}  Dinner={category_counts['Dinner']}")
if args.seed is not None:
    print(f"  Seed used: {args.seed} (reproducible)")