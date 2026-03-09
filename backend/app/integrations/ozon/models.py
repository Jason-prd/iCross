"""
Ozon Integration Data Models

Defines data structures for interacting with Ozon platform.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OzonProduct(BaseModel):
    """Ozon product model"""

    product_id: Optional[int] = Field(None, description="Ozon product ID")
    offer_id: str = Field(..., description="Merchant product ID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="SKU code")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Product price")
    old_price: Optional[float] = Field(None, description="Original price")
    marketing_price: Optional[float] = Field(None, description="Marketing price")
    vat: Optional[str] = Field(None, description="VAT rate")
    quantity: int = Field(0, description="Stock quantity")
    visibility: str = Field("INVISIBLE", description="Product visibility")
    category_id: Optional[int] = Field(None, description="Category ID")
    brand: Optional[str] = Field(None, description="Brand")
    barcode: Optional[str] = Field(None, description="Barcode")
    height: Optional[float] = Field(None, description="Height")
    width: Optional[float] = Field(None, description="Width")
    depth: Optional[float] = Field(None, description="Depth")
    dimension_unit: Optional[str] = Field("mm", description="Dimension unit")
    weight: Optional[float] = Field(None, description="Weight")
    weight_unit: Optional[str] = Field("g", description="Weight unit")
    images: List[str] = Field(default_factory=list, description="Product image URLs")
    images360: List[str] = Field(
        default_factory=list, description="360 degree image URLs"
    )
    color_image: Optional[str] = Field(None, description="Color image")
    attributes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Product attributes"
    )
    created_at: Optional[datetime] = Field(None, description="Created at")
    updated_at: Optional[datetime] = Field(None, description="Updated at")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonCategory(BaseModel):
    """Ozon category model"""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    has_children: bool = Field(False, description="Has children categories")
    description: Optional[str] = Field(None, description="Category description")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonOrder(BaseModel):
    """Ozon order model"""

    order_id: str = Field(..., description="Order ID")
    order_number: str = Field(..., description="Order number")
    status: str = Field(..., description="Order status")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    total_amount: float = Field(..., description="Total order amount")
    currency: str = Field("RUB", description="Currency")
    created_at: datetime = Field(..., description="Created at")
    updated_at: Optional[datetime] = Field(None, description="Updated at")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Order items")
    shipping_address: Optional[Dict[str, Any]] = Field(
        None, description="Shipping address"
    )
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonInventoryItem(BaseModel):
    """Ozon inventory item model"""

    product_id: int = Field(..., description="Product ID")
    offer_id: str = Field(..., description="Merchant product ID")
    sku: str = Field(..., description="SKU code")
    quantity: int = Field(0, description="Available stock")
    reserved_quantity: int = Field(0, description="Reserved stock")
    warehouse_id: Optional[int] = Field(None, description="Warehouse ID")
    updated_at: Optional[datetime] = Field(None, description="Updated at")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonWarehouse(BaseModel):
    """Ozon warehouse model"""

    warehouse_id: str = Field(..., description="Warehouse ID")
    name: str = Field(..., description="Warehouse name")
    is_fbos: bool = Field(False, description="Is FBOS warehouse")
    is_fbs: bool = Field(False, description="Is FBS warehouse")
    is_premium: bool = Field(False, description="Is Premium warehouse")
    type: Optional[str] = Field(None, description="Warehouse type")
    address: Optional[Dict[str, Any]] = Field(None, description="Warehouse address")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonDeliveryMethod(BaseModel):
    """Ozon delivery method model"""

    delivery_method_id: str = Field(..., description="Delivery method ID")
    name: str = Field(..., description="Delivery method name")
    warehouse_id: str = Field(..., description="Warehouse ID")
    warehouse_name: Optional[str] = Field(None, description="Warehouse name")
    price: float = Field(0, description="Delivery price")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonProductPrice(BaseModel):
    """Ozon product price model"""

    product_id: int = Field(..., description="Product ID")
    offer_id: str = Field(..., description="Merchant product ID")
    price: float = Field(..., description="Product price")
    old_price: Optional[float] = Field(None, description="Original price")
    marketing_price: Optional[float] = Field(None, description="Marketing price")
    currency: str = Field("RUB", description="Currency")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonProductStock(BaseModel):
    """Ozon product stock model"""

    product_id: int = Field(..., description="Product ID")
    offer_id: str = Field(..., description="Merchant product ID")
    stock: int = Field(0, description="Available stock")
    reserved_stock: int = Field(0, description="Reserved stock")
    warehouse_id: Optional[str] = Field(None, description="Warehouse ID")
    stock_type: Optional[str] = Field(None, description="Stock type")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True


class OzonSellerInfo(BaseModel):
    """Ozon seller info model"""

    seller_id: int = Field(..., description="Seller ID")
    name: str = Field(..., description="Seller name")
    company: str = Field(..., description="Company name")
    manager_id: Optional[int] = Field(None, description="Manager ID")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API data")

    class Config:
        arbitrary_types_allowed = True
