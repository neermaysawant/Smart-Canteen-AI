import sqlite3
import os

# build a robust path to the database file (relative to project root)
base_dir = os.path.dirname(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'canteen.db')

# connect to database (creates file if not exists)
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS canteen_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week TEXT,
    category TEXT,
    menu_item TEXT,
    is_exam_period INTEGER,
    plates_consumed INTEGER
)
''')

conn.commit()
conn.close()

print("Database and table created successfully!")