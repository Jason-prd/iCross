"""
Ozon Platform Integration Module

Provides API integration functionality with Ozon e-commerce platform,
including product management, category management, order synchronization, etc.
"""

from .adapter import OzonIntegrationAdapter
from .config import ozon_config
from .exceptions import OzonIntegrationError
from .models import OzonCategory, OzonInventoryItem, OzonOrder, OzonProduct

__version__ = "1.0.0"
__all__ = [
    "OzonIntegrationAdapter",
    "OzonProduct",
    "OzonCategory",
    "OzonOrder",
    "OzonInventoryItem",
    "ozon_config",
    "OzonIntegrationError",
]
