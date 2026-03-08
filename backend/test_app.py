# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

# Test app loading
print("Testing app loading...")

try:
    from app.main import app
    print("App loaded successfully!")
    
    # Check routes
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
            
except Exception as e:
    print(f"Error loading app: {e}")
    import traceback
    traceback.print_exc()
