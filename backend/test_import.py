#!/usr/bin/env python3
"""
Test Ozon API import
"""

import sys

sys.path.append("D:/iCross/python-ozon-api-main")

try:
    from ozon_api import OzonAPI
    from ozon_api.exceptions import OzonAPIError

    print("Successfully imported OzonAPI")
    print(f"OzonAPI: {OzonAPI}")
    print(f"OzonAPIError: {OzonAPIError}")
except ImportError as e:
    print(f"Import error: {e}")
    import traceback

    traceback.print_exc()

# Test adapter import
try:
    from app.integrations.ozon.adapter import OzonIntegrationAdapter

    print("Successfully imported OzonIntegrationAdapter")
except ImportError as e:
    print(f"Adapter import error: {e}")
    import traceback

    traceback.print_exc()
