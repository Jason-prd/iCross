# -*- coding: utf-8 -*-
"""
导入代发数据
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r'D:\iCross\backend')

import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from app.services.dropshipping import create_dropshipping_service

def main():
    # Load matched products data
    with open('matched_products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f"Loading {len(products_data)} products...")
    
    # Create service
    service = create_dropshipping_service()
    
    # Import from Excel
    result = service.import_from_excel(products_data)
    
    print(f"\n=== Import Complete ===")
    print(f"SPUs linked: {result['spus_linked']}")
    print(f"Products skipped: {result['skipped']}")
    print(f"Supplier ID: {result['supplier_id']}")
    
    # Get stats
    stats = service.get_dashboard_stats()
    print(f"\n=== Dropshipping Stats ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # Show sample links
    links = service.get_all_spu_links()
    print(f"\n=== Sample SPU Links ===")
    for link in links[:5]:
        print(f"  {link}")
    
    service.close()

if __name__ == '__main__':
    main()
