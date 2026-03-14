"""
Run this ONCE from your backend/ folder:
    python migrate_inventory.py

It will add the missing columns to your inventory table
without deleting any other data.
"""

import sqlite3
import os

# Adjust this path if needed
DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "cleveland.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check existing columns
cur.execute("PRAGMA table_info(inventory)")
existing_cols = [row[1] for row in cur.fetchall()]
print("Current columns:", existing_cols)

# Add missing columns (safe — won't fail if column already exists)
new_columns = [
    ("category",      "VARCHAR(100)"),
    ("unit",          "VARCHAR(50)"),
    ("unit_price",    "FLOAT DEFAULT 0.0"),
    ("reorder_level", "INTEGER DEFAULT 10"),
]

for col_name, col_type in new_columns:
    if col_name not in existing_cols:
        print(f"Adding column: {col_name}")
        cur.execute(f"ALTER TABLE inventory ADD COLUMN {col_name} {col_type}")
    else:
        print(f"Column already exists, skipping: {col_name}")

conn.commit()
conn.close()
print("\n✅ Done! Restart Flask and the error will be gone.")