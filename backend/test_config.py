#!/usr/bin/env python3
"""
Test Ozon config loading
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.integrations.ozon.config import ozon_config

print(f"OZON_CLIENT_ID from settings: {settings.OZON_CLIENT_ID}")
print(f"OZON_API_KEY from settings: {settings.OZON_API_KEY}")
print(f"ozon_config.client_id: {ozon_config.client_id}")
print(f"ozon_config.api_key: {ozon_config.api_key}")

# Check if they're None
if ozon_config.client_id is None:
    print("WARNING: ozon_config.client_id is None!")
if ozon_config.api_key is None:
    print("WARNING: ozon_config.api_key is None!")
