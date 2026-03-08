"""
Ozon集成数据模型

定义与Ozon平台交互的数据结构。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OzonProduct(BaseModel):
    """Ozon商品模型"""

    product_id: Optional[int] = Field(None, description="Ozon商品ID")
    offer_id: str = Field(..., description="商家商品ID（货号）")
    name: str = Field(..., description="商品名称")
    sku: str = Field(..., description="SKU编码")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., description="商品价格")
    old_price: Optional[float] = Field(None, description="商品原价")
    marketing_price: Optional[float] = Field(None, description="营销价格")
    vat: Optional[str] = Field(None, description="VAT税率")
    quantity: int = Field(0, description="库存数量")
    visibility: str = Field("INVISIBLE", description="商品可见性")
    category_id: Optional[int] = Field(None, description="分类ID")
    brand: Optional[str] = Field(None, description="品牌")
    barcode: Optional[str] = Field(None, description="条形码")
    height: Optional[float] = Field(None, description="高度")
    width: Optional[float] = Field(None, description="宽度")
    depth: Optional[float] = Field(None, description="深度")
    dimension_unit: Optional[str] = Field("mm", description="尺寸单位")
    weight: Optional[float] = Field(None, description="重量")
    weight_unit: Optional[str] = Field("g", description="重量单位")
    images: List[str] = Field(default_factory=list, description="商品图片URL列表")
    images360: List[str] = Field(default_factory=list, description="360度图片URL列表")
    color_image: Optional[str] = Field(None, description="颜色图片")
    attributes: List[Dict[str, Any]] = Field(default_factory=list, description="商品属性")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonCategory(BaseModel):
    """Ozon分类模型"""

    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    has_children: bool = Field(False, description="是否有子分类")
    description: Optional[str] = Field(None, description="分类描述")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonOrder(BaseModel):
    """Ozon订单模型"""

    order_id: str = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单号")
    status: str = Field(..., description="订单状态")
    customer_name: Optional[str] = Field(None, description="客户姓名")
    customer_email: Optional[str] = Field(None, description="客户邮箱")
    total_amount: float = Field(..., description="订单总金额")
    currency: str = Field("RUB", description="货币")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="订单商品")
    shipping_address: Optional[Dict[str, Any]] = Field(None, description="配送地址")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonInventoryItem(BaseModel):
    """Ozon库存项模型"""

    product_id: int = Field(..., description="商品ID")
    offer_id: str = Field(..., description="商家商品ID")
    sku: str = Field(..., description="SKU编码")
    quantity: int = Field(0, description="可用库存")
    reserved_quantity: int = Field(0, description="预留库存")
    warehouse_id: Optional[int] = Field(None, description="仓库ID")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonWarehouse(BaseModel):
    """Ozon仓库模型"""

    warehouse_id: str = Field(..., description="仓库ID")
    name: str = Field(..., description="仓库名称")
    is_fbos: bool = Field(False, description="是否为FBOS仓库")
    is_fbs: bool = Field(False, description="是否为FBS仓库")
    is_premium: bool = Field(False, description="是否为Premium仓库")
    type: Optional[str] = Field(None, description="仓库类型")
    address: Optional[Dict[str, Any]] = Field(None, description="仓库地址")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonDeliveryMethod(BaseModel):
    """Ozon配送方式模型"""

    delivery_method_id: str = Field(..., description="配送方式ID")
    name: str = Field(..., description="配送方式名称")
    warehouse_id: str = Field(..., description="仓库ID")
    warehouse_name: Optional[str] = Field(None, description="仓库名称")
    price: float = Field(0, description="配送价格")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonProductPrice(BaseModel):
    """Ozon商品价格模型"""

    product_id: int = Field(..., description="商品ID")
    offer_id: str = Field(..., description="商家商品ID")
    price: float = Field(..., description="商品价格")
    old_price: Optional[float] = Field(None, description="原价")
    marketing_price: Optional[float] = Field(None, description="促销价格")
    currency: str = Field("RUB", description="货币")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonProductStock(BaseModel):
    """Ozon商品库存模型"""

    product_id: int = Field(..., description="商品ID")
    offer_id: str = Field(..., description="商家商品ID")
    stock: int = Field(0, description="可用库存")
    reserved_stock: int = Field(0, description="预留库存")
    warehouse_id: Optional[str] = Field(None, description="仓库ID")
    stock_type: Optional[str] = Field(None, description="库存类型")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True


class OzonSellerInfo(BaseModel):
    """Ozon卖家信息模型"""

    seller_id: int = Field(..., description="卖家ID")
    name: str = Field(..., description="卖家名称")
    company: str = Field(..., description="公司名称")
    manager_id: Optional[int] = Field(None, description="经理ID")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API数据")

    class Config:
        arbitrary_types_allowed = True
