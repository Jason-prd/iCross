import sqlite3
conn = sqlite3.connect('D:/iCross/backend/icross_dev.db')
cur = conn.cursor()

# Check team_members
print("=== Team Members ===")
cur.execute("SELECT * FROM team_members")
for m in cur.fetchall():
    print(m)

# Check if admin user is in a team
print("\n=== Admin User ID ===")
cur.execute("SELECT id FROM users WHERE email = 'admin@icross.com'")
admin_id = cur.fetchone()
print(admin_id)

conn.close()
