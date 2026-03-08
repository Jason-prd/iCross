# -*- coding: utf-8 -*-
import sys
import json
from pathlib import Path

sys.path.insert(0, r'D:\iCross\backend')
sys.stdout.reconfigure(encoding='utf-8')

import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from app.services.automation import create_automation_service


def main():
    print("=" * 60)
    print("iCross Automation Flow Test")
    print("=" * 60)
    
    service = create_automation_service()
    
    # 1. Import selection data
    print("\n[Step 1] Import selection data...")
    try:
        with open('matched_products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        result = service.import_selected_products(products_data)
        print(f"  Done: {result['imported']} imported, {result['skipped']} skipped")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 2. Selection stats
    print("\n[Step 2] Selection status...")
    selection_stats = service.get_selection_stats()
    print(f"  Total: {selection_stats['total']}")
    print(f"  Draft: {selection_stats['draft']}")
    print(f"  Selected: {selection_stats['selected']}")
    
    # 3. Listing stats
    print("\n[Step 3] Listing status...")
    listing_stats = service.get_listing_stats()
    print(f"  Not listed: {listing_stats['not_listed']}")
    print(f"  Pending: {listing_stats['pending']}")
    print(f"  Listed: {listing_stats['listed']}")
    
    # 4. List selected products
    print("\n[Step 4] Selected products (top 5)...")
    selected = service.get_selected_products()
    for i, p in enumerate(selected[:5]):
        print(f"  {i+1}. SPU: {p.master_sku}")
        print(f"     Title: {p.title[:40]}...")
        print(f"     Cost: {p.source_price}")
        print(f"     Status: {p.listing_status}")
    
    # 5. Test listing
    print("\n[Step 5] Test listing...")
    if selected:
        test_product = selected[0]
        print(f"  Test product: {test_product.master_sku}")
        
        # Mark as pending
        service.update_product_listing_status(test_product.id, "pending")
        print(f"  Marked as pending")
        
        # Try to list
        result = service.list_product_on_ozon(test_product.id)
        if result.get("success"):
            print(f"  Listed successfully!")
            print(f"    Variants: {result.get('variants_count')}")
        else:
            print(f"  Result: {result.get('error')}")
    
    # 6. Final status
    print("\n[Final Status]")
    dashboard = service.get_dashboard()
    print(f"  Selection: {dashboard['selection']}")
    print(f"  Listing: {dashboard['listing']}")
    
    service.close()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
