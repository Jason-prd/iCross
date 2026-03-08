# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from pathlib import Path

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
    
    print(f"Using Client ID: {client_id}")
    print(f"Using API Key: {api_key[:10]}...")
    
    adapter = OzonIntegrationAdapter(
        client_id=client_id,
        api_key=api_key
    )
    async with adapter:
        result = await adapter.get_products(limit=100)
        print(f'\n=== Total products: {len(result)} ===\n')
        
        # Show first 20 products
        for i, p in enumerate(result[:20]):
            print(f"{i+1}. offer_id: {p.offer_id}")
            print(f"   product_id: {p.product_id}")
            print(f"   name: {p.name[:60]}...")
            print(f"   price: {p.price}")
            print(f"   quantity: {p.quantity}")
            print()

if __name__ == '__main__':
    asyncio.run(main())
