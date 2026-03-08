# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import os
os.environ['DATABASE_TYPE'] = 'sqlite'
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///./icross_dev.db')

# Add new columns
with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN selection_status VARCHAR(20) DEFAULT "draft"'))
        print('Added selection_status')
    except Exception as e:
        print(f'selection_status: {e}')
    
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN listing_status VARCHAR(20) DEFAULT "not_listed"'))
        print('Added listing_status')
    except Exception as e:
        print(f'listing_status: {e}')
    
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN source_url TEXT'))
        print('Added source_url')
    except Exception as e:
        print(f'source_url: {e}')
    
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN source_price FLOAT'))
        print('Added source_price')
    except Exception as e:
        print(f'source_price: {e}')
    
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN source_stock INTEGER'))
        print('Added source_stock')
    except Exception as e:
        print(f'source_stock: {e}')
    
    try:
        conn.execute(text('ALTER TABLE products ADD COLUMN source_supplier VARCHAR(100)'))
        print('Added source_supplier')
    except Exception as e:
        print(f'source_supplier: {e}')
    
    conn.commit()
    print('Done!')
