# -*- coding: utf-8 -*-
import requests

# Test each endpoint
base_url = "http://localhost:8000"

print("Testing selection/stats...")
try:
    r = requests.get(f"{base_url}/api/v1/selection/stats")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting dashboard/stats...")
try:
    r = requests.get(f"{base_url}/api/v1/dashboard/stats")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\nTesting selection (list)...")
try:
    r = requests.get(f"{base_url}/api/v1/selection?limit=5")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")
