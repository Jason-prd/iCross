# -*- coding: utf-8 -*-
import requests

# Test API
base_url = "http://localhost:8000"

# Test health
print("Testing health endpoint...")
r = requests.get(f"{base_url}/health")
print(f"  /health: {r.status_code} - {r.json()}")

# Test API prefix
print("\nTesting API endpoints...")
r = requests.get(f"{base_url}/api/v1/")
print(f"  /api/v1/: {r.status_code} - {r.json()}")

# Test selection stats
print("\nTesting selection stats...")
r = requests.get(f"{base_url}/api/v1/selection/stats")
print(f"  /api/v1/selection/stats: {r.status_code} - {r.text[:200]}")

# Test dashboard stats
print("\nTesting dashboard stats...")
r = requests.get(f"{base_url}/api/v1/dashboard/stats")
print(f"  /api/v1/dashboard/stats: {r.status_code} - {r.text[:200]}")
