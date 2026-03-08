# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from pathlib import Path
import json

# Set environment from .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add backend to path
sys.path.insert(0, r'D:\iCross\backend')

from app.integrations.ozon.adapter import OzonIntegrationAdapter

async def main():
    client_id = os.environ.get('OZON_CLIENT_ID')
    api_key = os.environ.get('OZON_API_KEY')
    
    adapter = OzonIntegrationAdapter(
        client_id=client_id,
        api_key=api_key
    )
    
    all_products = []
    offset = 0
    limit = 1000
    
    async with adapter:
        while True:
            print(f"Fetching products from offset {offset}...")
            
            from ozonapi.seller.schemas.products.v3__product_list import (
                ProductListFilter,
                ProductListRequest,
            )
            
            filter_obj = ProductListFilter(visibility="ALL")
            request = ProductListRequest(
                filter=filter_obj,
                limit=limit,
                offset=offset,
            )
            
            response = await adapter._api.product_list(request)
            
            if hasattr(response, 'result') and response.result:
                items = response.result.items if hasattr(response.result, 'items') else []
                total = response.result.total if hasattr(response.result, 'total') else 0
                
                if not items:
                    break
                    
                for item in items:
                    item_dict = item.model_dump() if hasattr(item, 'model_dump') else item
                    all_products.append(item_dict)
                
                print(f"Fetched {len(items)} products, total: {total}")
                
                if offset + limit >= total:
                    break
                offset += limit
            else:
                break
    
    print(f"\n=== Total products fetched: {len(all_products)} ===\n")
    
    # Show sample offer_ids
    print("Sample offer_ids:")
    for p in all_products[:30]:
        print(f"  {p.get('offer_id', 'N/A')}")
    
    # Save to file for later use
    with open('ozon_products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_products)} products to ozon_products.json")

if __name__ == '__main__':
    asyncio.run(main())
