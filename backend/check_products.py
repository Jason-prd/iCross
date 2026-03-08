# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('icross_dev.db')
cursor = conn.cursor()

# Get products table schema
cursor.execute("PRAGMA table_info(products)")
columns = cursor.fetchall()

print("Products table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check if team_id exists
has_team_id = any(col[1] == 'team_id' for col in columns)
print(f"\nHas team_id column: {has_team_id}")

# Check sample data
cursor.execute("SELECT id, master_sku, title, selection_status, listing_status FROM products LIMIT 3")
rows = cursor.fetchall()
print("\nSample products:")
for row in rows:
    print(f"  {row}")

conn.close()
