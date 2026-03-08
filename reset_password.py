import sqlite3
import hashlib

def hash_password(password: str) -> str:
    """Generate bcrypt-like hash (simplified for testing)"""
    # This is what the backend uses - we'll need to use the same method
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Let's check what the current hash looks like and create a known password
conn = sqlite3.connect('D:/iCross/backend/icross_dev.db')
cur = conn.cursor()

# Get admin user
cur.execute("SELECT id, password_hash FROM users WHERE email = 'admin@icross.com'")
user = cur.fetchone()
print(f"User: {user[0]}")
print(f"Current hash: {user[1]}")

# The password might be 'admin123' or something similar
# Let's just update to a known password using bcrypt
# First install bcrypt if needed
import subprocess
subprocess.run(['pip', 'install', 'bcrypt', '-q'])

import bcrypt
new_hash = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
cur.execute("UPDATE users SET password_hash = ? WHERE email = 'admin@icross.com'", (new_hash,))
conn.commit()
print("Password updated to: admin123")

conn.close()
