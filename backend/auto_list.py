# -*- coding: utf-8 -*-
"""
完整流程测试 - 自动上架所有已选品
"""
import sys
sys.path.insert(0, r'D:\iCross\backend')
import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from app.services.automation import create_automation_service

service = create_automation_service()

print("=" * 60)
print("Auto-Listing All Selected Products")
print("=" * 60)

# Get all selected products
selected = service.get_selected_products()
print(f"\nTotal selected products: {len(selected)}")

# Auto list them
result = service.auto_list_all_selected()

print(f"\nListing Results:")
print(f"  Total: {result['total']}")
print(f"  Success: {result['success']}")
print(f"  Failed: {result['failed']}")

# Final status
print("\n" + "=" * 60)
print("FINAL STATUS")
print("=" * 60)

dashboard = service.get_dashboard()

print("\n[Selection Status]")
for k, v in dashboard["selection"].items():
    print(f"  {k}: {v}")

print("\n[Listing Status]")
for k, v in dashboard["listing"].items():
    print(f"  {k}: {v}")

# Show first 10 listed products
listed = service.get_listed_products()
print(f"\n[Listed Products (top 10)]")
for i, p in enumerate(listed[:10]):
    print(f"  {i+1}. {p.master_sku} - {p.title[:40]}...")

service.close()

print("\n" + "=" * 60)
print("COMPLETE!")
print("=" * 60)
