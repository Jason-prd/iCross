import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai")
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team_memberships: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="user", foreign_keys="TeamMember.user_id"
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user"
    )


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str] = mapped_column(Text, nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    subscription_plan: Mapped[str] = mapped_column(String(20), default="basic")
    subscription_status: Mapped[str] = mapped_column(String(20), default="active")
    max_members: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    members: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="team"
    )
    shops: Mapped[list["Shop"]] = relationship("Shop", back_populates="team")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="team")
    warehouses: Mapped[list["Warehouse"]] = relationship(
        "Warehouse", back_populates="team"
    )
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="team"
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")
    invited_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship(
        "User", back_populates="team_memberships", foreign_keys=[user_id]
    )
    inviter: Mapped["User"] = relationship("User", foreign_keys=[invited_by])


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    device_info: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_shop_id: Mapped[str] = mapped_column(String(100), nullable=True)
    platform_shop_name: Mapped[str] = mapped_column(String(100), nullable=True)
    api_credentials: Mapped[dict] = mapped_column(JSON, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    sync_settings: Mapped[dict] = mapped_column(
        JSON,
        default={
            "product_sync_interval": 120,
            "order_sync_interval": 5,
            "inventory_sync_interval": 30,
            "sync_enabled": True,
        },
    )
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_sync_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync_status: Mapped[str] = mapped_column(String(20), nullable=True)
    api_quota_used: Mapped[int] = mapped_column(Integer, default=0)
    api_quota_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    api_quota_reset_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    shop_extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team", back_populates="shops")
    products: Mapped[list["PlatformProduct"]] = relationship(
        "PlatformProduct", back_populates="shop"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="shop")
    sync_logs: Mapped[list["ShopSyncLog"]] = relationship(
        "ShopSyncLog", back_populates="shop"
    )


class ShopSyncLog(Base):
    __tablename__ = "shop_sync_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    sync_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sync_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    items_total: Mapped[int] = mapped_column(Integer, default=0)
    items_processed: Mapped[int] = mapped_column(Integer, default=0)
    items_succeeded: Mapped[int] = mapped_column(Integer, default=0)
    items_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    shop: Mapped["Shop"] = relationship("Shop", back_populates="sync_logs")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    master_sku: Mapped[str] = mapped_column(String(100), nullable=False)  # SPU
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    main_image_url: Mapped[str] = mapped_column(Text, nullable=True)
    images: Mapped[list] = mapped_column(JSON, default=list)
    category_id: Mapped[str] = mapped_column(String(36), nullable=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    dimensions: Mapped[dict] = mapped_column(JSON, nullable=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # 选品状态
    selection_status: Mapped[str] = mapped_column(
        String(20), default="draft",
        comment="选品状态: draft-未选品, selected-已选品"
    )
    
    # 上架状态
    listing_status: Mapped[str] = mapped_column(
        String(20), default="not_listed",
        comment="上架状态: not_listed-未上架, pending-待上架, listing-上架中, listed-已上架"
    )
    
    # 1688选品链接
    source_url: Mapped[str] = mapped_column(Text, nullable=True, comment="1688选品链接")
    source_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True, comment="采购价")
    source_stock: Mapped[int] = mapped_column(Integer, nullable=True, comment="源库存")
    source_supplier: Mapped[str] = mapped_column(String(100), nullable=True, comment="供应商")
    
    tags: Mapped[list] = mapped_column(JSON, default=list)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team", back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )
    platform_products: Mapped[list["PlatformProduct"]] = relationship(
        "PlatformProduct", back_populates="product"
    )
    inventory: Mapped[list["Inventory"]] = relationship(
        "Inventory", back_populates="product"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    compare_at_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    barcode: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    platform_products: Mapped[list["PlatformProduct"]] = relationship(
        "PlatformProduct", back_populates="variant"
    )
    inventory: Mapped[list["Inventory"]] = relationship(
        "Inventory", back_populates="variant"
    )


class PlatformProduct(Base):
    __tablename__ = "platform_products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    platform_product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    platform_sku: Mapped[str] = mapped_column(String(100), nullable=True)
    platform_title: Mapped[str] = mapped_column(String(255), nullable=True)
    platform_description: Mapped[str] = mapped_column(Text, nullable=True)
    platform_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    platform_currency: Mapped[str] = mapped_column(String(3), nullable=True)
    platform_stock: Mapped[int] = mapped_column(Integer, default=0)
    platform_status: Mapped[str] = mapped_column(String(50), nullable=True)
    platform_url: Mapped[str] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_status: Mapped[str] = mapped_column(String(20), default="synced")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="platform_products"
    )
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant", back_populates="platform_products"
    )
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    platform_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    order_number: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), nullable=True
    )
    customer_name: Mapped[str] = mapped_column(String(100), nullable=True)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    shipping_address: Mapped[dict] = mapped_column(JSON, nullable=False)
    billing_address: Mapped[dict] = mapped_column(JSON, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)
    payment_transaction_id: Mapped[str] = mapped_column(String(100), nullable=True)
    fulfillment_status: Mapped[str] = mapped_column(String(20), default="unfulfilled")
    shipping_carrier: Mapped[str] = mapped_column(String(100), nullable=True)
    shipping_tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)
    shipped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    platform_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    platform_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
    shop: Mapped["Shop"] = relationship("Shop", back_populates="orders")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=True
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id"), nullable=True
    )
    platform_product_id: Mapped[str] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    substatus: Mapped[str] = mapped_column(String(50), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    order: Mapped["Order"] = relationship("Order", back_populates="status_history")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="physical")
    address: Mapped[dict] = mapped_column(JSON, nullable=True)
    contact_info: Mapped[dict] = mapped_column(JSON, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team", back_populates="warehouses")
    inventory: Mapped[list["Inventory"]] = relationship(
        "Inventory", back_populates="warehouse"
    )
    transactions: Mapped[list["InventoryTransaction"]] = relationship(
        "InventoryTransaction", back_populates="warehouse"
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=True)
    reorder_quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    last_counted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
    product: Mapped["Product"] = relationship("Product", back_populates="inventory")
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant", back_populates="inventory"
    )
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="inventory"
    )
    transactions: Mapped[list["InventoryTransaction"]] = relationship(
        "InventoryTransaction", back_populates="inventory"
    )
    alerts: Mapped[list["InventoryAlert"]] = relationship(
        "InventoryAlert", back_populates="inventory"
    )


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    inventory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    new_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[str] = mapped_column(String(36), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
    product: Mapped["Product"] = relationship("Product")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant")
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="transactions"
    )
    inventory: Mapped["Inventory"] = relationship(
        "Inventory", back_populates="transactions"
    )


class InventoryAlert(Base):
    __tablename__ = "inventory_alerts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    inventory_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True
    )
    warehouse_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True
    )
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=True)
    current_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="alerts")
    team: Mapped["Team"] = relationship("Team")
    product: Mapped["Product"] = relationship("Product")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    company: Mapped[str] = mapped_column(String(100), nullable=True)
    shipping_address: Mapped[dict] = mapped_column(JSON, nullable=True)
    billing_address: Mapped[dict] = mapped_column(JSON, nullable=True)
    customer_type: Mapped[str] = mapped_column(String(20), default="retail")
    level: Mapped[str] = mapped_column(String(20), default="normal")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    first_order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team", back_populates="customers")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="customer")
    communications: Mapped[list["CustomerCommunication"]] = relationship(
        "CustomerCommunication", back_populates="customer"
    )


class CustomerCommunication(Base):
    __tablename__ = "customer_communications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    follow_up_action: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attachments: Mapped[list] = mapped_column(JSON, default=list)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="communications"
    )


class OzonProduct(Base):
    __tablename__ = "ozon_products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False
    )
    ozon_product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ozon_sku: Mapped[int] = mapped_column(Integer, nullable=True)
    offer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, nullable=True)
    category_name: Mapped[str] = mapped_column(String(255), nullable=True)
    type_id: Mapped[int] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    old_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    marketing_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    reserved_stock: Mapped[int] = mapped_column(Integer, default=0)
    stock_type: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)
    status_name: Mapped[str] = mapped_column(String(100), nullable=True)
    moderate_status: Mapped[str] = mapped_column(String(50), nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), default="INVISIBLE")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    is_discounted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_super: Mapped[bool] = mapped_column(Boolean, default=False)
    vat: Mapped[str] = mapped_column(String(20), nullable=True)
    commission_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    volume_weight: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    barcodes: Mapped[list] = mapped_column(JSON, default=list)
    images: Mapped[list] = mapped_column(JSON, default=list)
    primary_image: Mapped[str] = mapped_column(Text, nullable=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict)
    platform_url: Mapped[str] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_status: Mapped[str] = mapped_column(String(20), default="synced")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
    shop: Mapped["Shop"] = relationship("Shop")


class OzonCategoryTree(Base):
    """Ozon商品分类树"""
    __tablename__ = "ozon_category_tree"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=True
    )
    description_category_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(255), nullable=True)
    category_name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    category_name_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    category_name_zh: Mapped[str] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    type_id: Mapped[int] = mapped_column(Integer, nullable=True)
    type_name: Mapped[str] = mapped_column(String(255), nullable=True)
    type_name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    type_name_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    type_name_zh: Mapped[str] = mapped_column(String(255), nullable=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    children: Mapped[list] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")


class OzonCategoryAttribute(Base):
    """Ozon分类属性"""
    __tablename__ = "ozon_category_attributes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=True
    )
    description_category_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute_name: Mapped[str] = mapped_column(String(255), nullable=True)
    attribute_name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    attribute_name_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    attribute_name_zh: Mapped[str] = mapped_column(String(255), nullable=True)
    attribute_description: Mapped[str] = mapped_column(Text, nullable=True)
    attribute_type: Mapped[str] = mapped_column(String(50), nullable=True)
    group_id: Mapped[int] = mapped_column(Integer, nullable=True)
    group_name: Mapped[str] = mapped_column(String(255), nullable=True)
    group_name_en: Mapped[str] = mapped_column(String(255), nullable=True)
    group_name_ru: Mapped[str] = mapped_column(String(255), nullable=True)
    group_name_zh: Mapped[str] = mapped_column(String(255), nullable=True)
    dictionary_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    is_aspect: Mapped[bool] = mapped_column(Boolean, default=False)
    is_collection: Mapped[bool] = mapped_column(Boolean, default=False)
    category_dependent: Mapped[bool] = mapped_column(Boolean, default=False)
    max_value_count: Mapped[int] = mapped_column(Integer, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")


class OzonAttributeValue(Base):
    """Ozon属性值"""
    __tablename__ = "ozon_attribute_values"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    shop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=True
    )
    description_category_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=True)
    value_en: Mapped[str] = mapped_column(String(500), nullable=True)
    value_ru: Mapped[str] = mapped_column(String(500), nullable=True)
    value_zh: Mapped[str] = mapped_column(String(500), nullable=True)
    info: Mapped[str] = mapped_column(Text, nullable=True)
    picture: Mapped[str] = mapped_column(Text, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    team: Mapped["Team"] = relationship("Team")
