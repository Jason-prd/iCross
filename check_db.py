import sqlite3
conn = sqlite3.connect('D:/iCross/backend/icross_dev.db')
cur = conn.cursor()

# Check users table structure
print("=== Users Table ===")
cur.execute("PRAGMA table_info(users)")
print(cur.fetchall())

cur.execute("SELECT * FROM users LIMIT 3")
for u in cur.fetchall():
    print(u)

# Check shops
print("\n=== Shops ===")
cur.execute("SELECT id, name, platform FROM shops")
for s in cur.fetchall():
    print(s)

# Check products count
print("\n=== Products ===")
cur.execute("SELECT COUNT(*) FROM products")
print(f"Total: {cur.fetchone()[0]}")

# Check ozon_products count
print("\n=== Ozon Products ===")
cur.execute("SELECT COUNT(*) FROM ozon_products")
print(f"Total: {cur.fetchone()[0]}")

# Check orders
print("\n=== Orders ===")
cur.execute("SELECT COUNT(*) FROM orders")
print(f"Total: {cur.fetchone()[0]}")

conn.close()
