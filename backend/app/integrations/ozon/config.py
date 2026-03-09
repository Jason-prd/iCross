"""
Ozon Integration Config

Manages configuration parameters for Ozon platform integration.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.core.config import settings


class OzonConfig(BaseModel):
    """Ozon integration config model"""

    # API credentials
    client_id: str = Field(default_factory=lambda: settings.OZON_CLIENT_ID)
    api_key: str = Field(default_factory=lambda: settings.OZON_API_KEY)
    api_url: str = Field(default="https://api-seller.ozon.ru")

    # Sync settings
    sync_interval_minutes: int = Field(default=30, ge=5, le=1440)
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: int = Field(default=5, ge=1, le=60)

    # Feature toggles
    sync_products: bool = Field(default=True)
    sync_orders: bool = Field(default=True)
    sync_inventory: bool = Field(default=True)
    push_inventory_updates: bool = Field(default=True)

    # Limit settings
    max_products_per_request: int = Field(default=1000, ge=1, le=1000)
    max_orders_per_request: int = Field(default=100, ge=1, le=1000)
    request_timeout_seconds: int = Field(default=30, ge=5, le=300)

    # Advanced settings
    enable_rate_limiting: bool = Field(default=True)
    enable_request_logging: bool = Field(default=True)
    enable_error_notifications: bool = Field(default=True)

    # Custom endpoints (for testing or special environments)
    custom_endpoints: Optional[dict] = Field(
        default_factory=dict, description="Custom API endpoint mapping"
    )

    class Config:
        env_prefix = "OZON_"


# Global config instance
ozon_config = OzonConfig()
