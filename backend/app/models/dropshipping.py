# -*- coding: utf-8 -*-
"""
iCross 一键代发模块 - 数据模型
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
    """代发商/供应商"""
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), default="1688")  # 1688, taobao, etc.
    contact_name: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    contact_wechat: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_address: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product_links: Mapped[list["ProductSupplierLink"]] = relationship(
        "ProductSupplierLink", back_populates="supplier"
    )


class ProductSupplierLink(Base):
    """商品与代发商关联 (SPU级别)"""
    __tablename__ = "product_supplier_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    spu: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # SPU编号，如 SKU#0918392810
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=True)  # 可选关联到产品
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=True)  # 可选关联到变体
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=False)
    
    # 代发商品信息
    supplier_product_url: Mapped[str] = mapped_column(Text, nullable=True)  # 1688商品链接
    supplier_product_id: Mapped[str] = mapped_column(String(100), nullable=True)  # 1688商品ID
    supplier_sku: Mapped[str] = mapped_column(String(100), nullable=True)  # 代发SKU
    purchase_cost: Mapped[float] = mapped_column(Float, nullable=True)  # 采购成本
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=True)  # 采购运费
    
    # 仓库信息
    warehouse: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_contact: Mapped[str] = mapped_column(String(100), nullable=True)
    warehouse_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 状态
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否首选代发商
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="product_links")
    product: Mapped["Product"] = relationship("Product")


class DropshipOrder(Base):
    """代发订单"""
    __tablename__ = "dropship_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(36), ForeignKey("shops.id"), nullable=False)
    
    # 关联的Ozon订单
    platform_order_id: Mapped[str] = mapped_column(String(100), nullable=False)  # Ozon订单ID
    platform_order_number: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # 商品信息
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    
    # 代发商信息
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    supplier_order_id: Mapped[str] = mapped_column(String(100), nullable=True)  # 代发商订单号
    
    # 费用
    purchase_cost: Mapped[float] = mapped_column(Float, default=0)  # 采购成本
    shipping_cost: Mapped[float] = mapped_column(Float, default=0)  # 运费
    total_cost: Mapped[float] = mapped_column(Float, default=0)  # 总成本
    
    # 销售
    sale_price: Mapped[float] = mapped_column(Float, default=0)  # 销售价
    profit: Mapped[float] = mapped_column(Float, default=0)  # 利润
    
    # 物流
    tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)
    shipping_carrier: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, shipped, cancelled
    auto_dropship: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否自动代发
    
    # 时间戳
    order_placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Ozon下单时间
    supplier_order_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # 代发下单时间
    shipped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # 发货时间
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # 送达时间
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DropshipSettings(Base):
    """代发设置"""
    __tablename__ = "dropship_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    team_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    
    # 自动代发开关
    auto_dropship_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 同步设置
    order_sync_interval: Mapped[int] = mapped_column(Integer, default=5)  # 分钟
    inventory_sync_interval: Mapped[int] = mapped_column(Integer, default=30)  # 分钟
    
    # 预警设置
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    price_change_threshold: Mapped[float] = mapped_column(Float, default=20)  # 百分比
    
    # 通知设置
    notify_on_order: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_shipment: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_exception: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
