# -*- coding: utf-8 -*-
"""
导入Excel匹配的商品数据到iCross系统 (SQLite版本)
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, r'D:\iCross\backend')

# Set environment for SQLite
import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Product, ProductVariant, PlatformProduct, Shop, Base
from app.core.config import settings

# Use sync SQLite for simpler import
DATABASE_URL = "sqlite:///./icross_dev.db"

def import_products():
    """Import matched products to iCross database"""
    
    # Load matched products data
    with open('matched_products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f"Loading {len(products_data)} matched products...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if shop exists
        shop = session.query(Shop).first()
        
        if not shop:
            print("Creating default shop...")
            shop = Shop(
                id="default-shop",
                team_id="default-team",
                name="Ozon Main Shop",
                platform="ozon",
                platform_shop_id="2867211",
                platform_shop_name="Ozon店铺",
                api_credentials={
                    "client_id": os.environ.get('OZON_CLIENT_ID', '2867211'),
                    "api_key": os.environ.get('OZON_API_KEY', '')
                },
                sync_settings={
                    "product_sync_interval": 120,
                    "order_sync_interval": 5,
                    "inventory_sync_interval": 30,
                    "sync_enabled": True
                }
            )
            session.add(shop)
            session.commit()
            print(f"Created shop: {shop.id}")
        else:
            print(f"Using existing shop: {shop.id}")
        
        shop_id = shop.id
        
        # Import products
        imported_count = 0
        skipped_count = 0
        
        for i, product_info in enumerate(products_data):
            try:
                sku = product_info.get('sku', '')
                if not sku:
                    skipped_count += 1
                    continue
                
                # Check if product already exists
                existing = session.query(PlatformProduct).filter_by(platform_sku=sku).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Generate unique IDs
                sku_hash = sku.replace('#', '').replace('-', '')[:20]
                product_id = f"prod-{sku_hash}"
                variant_id = f"var-{sku_hash}"
                
                # Create main product
                product = Product(
                    id=product_id,
                    team_id="default-team",
                    master_sku=sku,
                    title=product_info.get('ozon_name', product_info.get('1688_name', 'Unknown'))[:255] or "Unknown Product",
                    description=product_info.get('ozon_name_ru', ''),
                    main_image_url="",
                    images=[],
                    brand="",
                    weight=float(product_info.get('weight_g', 0)) if product_info.get('weight_g') else None,
                    status="active",
                    extra_data={
                        "1688_name": product_info.get('1688_name', ''),
                        "category": product_info.get('category', ''),
                        "city": product_info.get('city', ''),
                        "1688_link": product_info.get('1688_link', ''),
                    }
                )
                
                session.add(product)
                
                # Create product variant (SKU level)
                variant = ProductVariant(
                    id=variant_id,
                    product_id=product_id,
                    sku=sku,
                    variant_attributes={
                        "sku_name": product_info.get('sku_name', ''),
                        "color": "",
                        "size": ""
                    },
                    price=float(product_info.get('price_cny', 0)) if product_info.get('price_cny') else 0,
                    cost=float(product_info.get('purchase_cost', 0)) if product_info.get('purchase_cost') else 0,
                    status="active"
                )
                
                session.add(variant)
                
                # Create platform product (Ozon)
                ozon_product_id = product_info.get('ozon_product_id', '')
                platform_product = PlatformProduct(
                    id=f"pp-{sku_hash}",
                    product_id=product_id,
                    variant_id=variant_id,
                    shop_id=shop_id,
                    platform_product_id=str(ozon_product_id) if ozon_product_id else sku,
                    platform_sku=sku,
                    platform_title=product_info.get('ozon_name', '')[:255] if product_info.get('ozon_name') else "Unknown",
                    platform_price=float(product_info.get('ozon_price', 0)) if product_info.get('ozon_price') else 0,
                    platform_stock=int(product_info.get('ozon_quantity', 0)) if product_info.get('ozon_quantity') else 0,
                    platform_status="active",
                    platform_url=f"https://www.ozon.ru/product/{ozon_product_id}/" if ozon_product_id else "",
                    last_synced_at=datetime.utcnow(),
                    sync_status="synced"
                )
                
                session.add(platform_product)
                
                imported_count += 1
                
                if imported_count % 50 == 0:
                    session.commit()
                    print(f"Imported {imported_count} products...")
                    
            except Exception as e:
                print(f"Error importing {product_info.get('sku')}: {e}")
                continue
        
        # Final commit
        session.commit()
        
        print(f"\n=== Import Complete ===")
        print(f"Total products imported: {imported_count}")
        print(f"Products skipped (already exists): {skipped_count}")
        print(f"Shop ID: {shop_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    import_products()
