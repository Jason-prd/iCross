# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import os
os.environ['DATABASE_TYPE'] = 'sqlite'
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///./icross_dev.db')

# Drop and recreate table
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS product_supplier_links'))
    conn.commit()

print('Table dropped, recreating...')

# Recreate tables
from app.core.database import Base
from app.models.dropshipping import Supplier, ProductSupplierLink, DropshipOrder, DropshipSettings
Base.metadata.create_all(engine)

print('Done!')
