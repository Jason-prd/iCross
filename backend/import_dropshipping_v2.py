# -*- coding: utf-8 -*-
"""
导入代发数据 (带NaN处理)
"""
import json
import sys
import math
from pathlib import Path

sys.path.insert(0, r'D:\iCross\backend')

import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from app.services.dropshipping import create_dropshipping_service

def safe_float(value, default=0):
    """安全转换浮点数"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        if math.isnan(value) or math.isinf(value):
            return default
        return float(value)
    try:
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except:
        return default

def safe_str(value, default=""):
    """安全转换字符串"""
    if value is None:
        return default
    if isinstance(value, str):
        if value.lower() in ['nan', 'none', 'null', '']:
            return default
        return value
    return str(value)

def main():
    # Load matched products data
    with open('matched_products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f"Loading {len(products_data)} products...")
    
    # Create service
    service = create_dropshipping_service()
    
    # Import from Excel with safe parsing
    linked_spus = set()
    skipped = 0
    
    supplier = service.session.query(service.session.query(
        service.session.query(service.session.query.__self__.__class__).filter_by).first().__class__
    
    # Simpler approach - just use the service's import method with fixed data
    fixed_data = []
    for product_info in products_data:
        fixed_product = {
            "sku": safe_str(product_info.get("sku", "")),
            "purchase_cost": safe_float(product_info.get("purchase_cost", 0)),
            "shipping_cost": safe_float(product_info.get("shipping_cost", 0)),
            "city": safe_str(product_info.get("city", "")),
            "1688_link": safe_str(product_info.get("1688_link", "")),
        }
        fixed_data.append(fixed_product)
    
    result = service.import_from_excel(fixed_data)
    
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
