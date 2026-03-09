# -*- coding: utf-8 -*-
"""
iCross One-Click Dropship Module - Data Models
"""

from datetime import datetime
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Supplier(Base):
    """Supplier/Dropshipper"""

    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(
        String(20), default="1688"
    )  # 1688, taobao, etc.
    contact_name: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    contact_wechat: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_address: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    product_links: Mapped[list["ProductSupplierLink"]] = relationship(
        "ProductSupplierLink", back_populates="supplier"
    )


class ProductSupplierLink(Base):
    """Product and Supplier Link (SPU Level)"""

    __tablename__ = "product_supplier_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    spu: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # SPU number, e.g. SKU#0918392810
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=True
    )  # Optional link to product
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id"), nullable=True
    )  # Optional link to variant
    supplier_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("suppliers.id"), nullable=False
    )

    # Dropship product info
    supplier_product_url: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # 1688 product link
    supplier_product_id: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # 1688 product ID
    supplier_sku: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # Dropship SKU
    purchase_cost: Mapped[float] = mapped_column(Float, nullable=True)  # Purchase cost
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=True)  # Shipping cost

    # Warehouse info
    warehouse: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_contact: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_phone: Mapped[str] = mapped_column(String(50), nullable=True)

    # Status
    is_preferred: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Preferred dropshipper
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="product_links"
    )
    product: Mapped["Product"] = relationship("Product")


class DropshipOrder(Base):
    """Dropship order"""

    __tablename__ = "dropship_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id"), nullable=False
    )

    # Related Ozon order
    platform_order_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Ozon order ID
    platform_order_number: Mapped[str] = mapped_column(String(100), nullable=True)

    # Product info
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=False
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id"), nullable=True
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Supplier info
    supplier_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("suppliers.id"), nullable=True
    )
    supplier_order_id: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # Supplier order number

    # Cost
    purchase_cost: Mapped[float] = mapped_column(Float, default=0)  # Purchase cost
    shipping_cost: Mapped[float] = mapped_column(Float, default=0)  # Shipping cost
    total_cost: Mapped[float] = mapped_column(Float, default=0)  # Total cost

    # Sales
    sale_price: Mapped[float] = mapped_column(Float, default=0)  # Sale price
    profit: Mapped[float] = mapped_column(Float, default=0)  # Profit

    # Logistics
    tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)
    shipping_carrier: Mapped[str] = mapped_column(String(50), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, processing, shipped, cancelled
    auto_dropship: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # Auto dropship enabled

    # Timestamps
    order_placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Ozon order time
    supplier_order_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Supplier order time
    shipped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Shipped time
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Delivered time

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class DropshipSettings(Base):
    """Dropship settings"""

    __tablename__ = "dropship_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    # Auto dropship toggle
    auto_dropship_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Sync settings
    order_sync_interval: Mapped[int] = mapped_column(Integer, default=5)  # minutes
    inventory_sync_interval: Mapped[int] = mapped_column(Integer, default=30)  # minutes

    # Alert settings
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    price_change_threshold: Mapped[float] = mapped_column(
        Float, default=20
    )  # percentage

    # Notification settings
    notify_on_order: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_shipment: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_exception: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
