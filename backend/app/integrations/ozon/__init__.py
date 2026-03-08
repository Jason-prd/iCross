"""
Ozon平台集成模块

提供与Ozon电商平台的API集成功能，包括商品管理、分类管理、订单同步等。
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
