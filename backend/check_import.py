# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\iCross\backend')

import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Product, ProductVariant, PlatformProduct, Shop

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Count records
products_count = session.query(Product).count()
variants_count = session.query(ProductVariant).count()
platform_products_count = session.query(PlatformProduct).count()
shops_count = session.query(Shop).count()

print(f"=== iCross Database Summary ===")
print(f"Shops: {shops_count}")
print(f"Products: {products_count}")
print(f"Product Variants: {variants_count}")
print(f"Platform Products: {platform_products_count}")

# Show sample products
print(f"\n=== Sample Products ===")
products = session.query(Product).limit(5).all()
for p in products:
    print(f"\nProduct: {p.master_sku}")
    print(f"  Title: {p.title[:50]}...")
    print(f"  Price: {p.variants[0].price if p.variants else 'N/A'}")
    print(f"  Cost: {p.variants[0].cost if p.variants else 'N/A'}")
    if p.platform_products:
        pp = p.platform_products[0]
        print(f"  Ozon ID: {pp.platform_product_id}")
        print(f"  Ozon SKU: {pp.platform_sku}")
        print(f"  Ozon Price: {pp.platform_price}")
        print(f"  Ozon Stock: {pp.platform_stock}")

session.close()
