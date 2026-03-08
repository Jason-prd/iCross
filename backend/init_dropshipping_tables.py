# -*- coding: utf-8 -*-
"""
初始化代发模块的数据库表
"""
import sys
sys.path.insert(0, r'D:\iCross\backend')

import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from sqlalchemy import create_engine
from app.core.database import Base
from app.models.dropshipping import Supplier, ProductSupplierLink, DropshipOrder, DropshipSettings

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=True)

# Create all new tables
print("Creating dropshipping tables...")
Base.metadata.create_all(engine)

print("Done!")
