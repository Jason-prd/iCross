# -*- coding: utf-8 -*-
"""
修复: 将已选品与已有变体关联
"""
import sys
sys.path.insert(0, r'D:\iCross\backend')
import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Product, ProductVariant
from app.services.spu_utils import extract_spu

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

print("Fixing selected products with variants...")

# Get all selected products
selected_products = session.query(Product).filter_by(
    selection_status="selected"
).all()

print(f"Found {len(selected_products)} selected products")

fixed = 0
for product in selected_products:
    spu = product.master_sku
    
    # Find variants with matching SPU
    # The variant sku should start with the SPU
    spu_num = spu.replace("SKU#", "")
    variants = session.query(ProductVariant).filter(
        ProductVariant.sku.like(f"SKU#{spu_num}%")
    ).all()
    
    if variants:
        print(f"  {spu}: found {len(variants)} variants")
        fixed += 1
    else:
        print(f"  {spu}: NO variants found")

print(f"\nFixed: {fixed} products have variants")

# Now let's link them properly
for product in selected_products:
    spu = product.master_sku
    spu_num = spu.replace("SKU#", "")
    
    variants = session.query(ProductVariant).filter(
        ProductVariant.sku.like(f"SKU#{spu_num}%")
    ).all()
    
    if variants:
        # Update the product with first variant info
        variant = variants[0]
        product.source_price = variant.cost or product.source_price
        
        # Link variants to this product
        for v in variants:
            if v.product_id != product.id:
                v.product_id = product.id
        
        if fixed <= 5:  # Show first 5
            print(f"  Linked {spu} with {len(variants)} variants")

session.commit()
print("\nDone!")
