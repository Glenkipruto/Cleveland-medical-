import sqlite3
import os

DB_PATH = r"D:\Cleveland medical college\backend\instance\cleveland.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Drop and recreate inventory table with all correct columns
cur.execute("DROP TABLE IF EXISTS inventory")
cur.execute("""
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        category VARCHAR(100),
        unit VARCHAR(50),
        quantity INTEGER DEFAULT 0,
        unit_price FLOAT DEFAULT 0.0,
        reorder_level INTEGER DEFAULT 10,
        date_added DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print("✅ inventory table recreated with all columns. Restart Flask now.")