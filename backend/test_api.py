# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

# Test imports
try:
    from app.api.v1.endpoints import selection
    print("Selection module: OK")
except Exception as e:
    print(f"Selection module: {e}")

try:
    from app.api.v1.endpoints import dropship
    print("Dropship module: OK")
except Exception as e:
    print(f"Dropship module: {e}")

try:
    from app.api.v1.endpoints import dashboard
    print("Dashboard module: OK")
except Exception as e:
    print(f"Dashboard module: {e}")

# Test database
import os
os.environ['DATABASE_TYPE'] = 'sqlite'

try:
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///./icross_dev.db')
    result = engine.execute("SELECT COUNT(*) FROM products").fetchone()
    print(f"Products in DB: {result[0]}")
except Exception as e:
    print(f"Database error: {e}")
