# -*- coding: utf-8 -*-
"""
iCross 商品状态管理
定义商品的生命周期状态
"""

from enum import Enum


class ProductStatus(str, Enum):
    """商品状态枚举"""
    
    # 选品阶段
    DRAFT = "draft"              # 草稿/未选品
    SELECTED = "selected"         # 已选品（待上架）
    
    # 上架阶段
    LISTING = "listing"          # 上架中
    LISTED = "listed"            # 已上架
    
    # 销售阶段
    OUT_OF_STOCK = "out_of_stock"  # 缺货
    ARCHIVED = "archived"        # 已归档
    
    # 异常
    ERROR = "error"              # 异常


class ListingStatus(str, Enum):
    """上架状态"""
    
    NOT_LISTED = "not_listed"       # 未上架
    PENDING = "pending"              # 待上架
    LISTING = "listing"              # 上架中
    LISTED = "listed"                # 已上架
    DELISTED = "delisted"            # 已下架
    ARCHIVED = "archived"            # 已归档


# 状态显示名称
STATUS_DISPLAY = {
    "draft": "未选品",
    "selected": "已选品",
    "listing": "上架中",
    "listed": "已上架",
    "out_of_stock": "缺货",
    "archived": "已归档",
    "error": "异常",
    "not_listed": "未上架",
    "pending": "待上架",
    "delisted": "已下架",
}

# 状态流程
STATUS_FLOW = {
    "draft": ["selected", "error"],
    "selected": ["listing", "archived", "error"],
    "listing": ["listed", "error"],
    "listed": ["out_of_stock", "delisted", "archived", "error"],
    "out_of_stock": ["listed", "archived"],
    "delisted": ["listed", "archived"],
    "archived": [],
    "error": ["draft", "selected"],
}


def can_transition(from_status: str, to_status: str) -> bool:
    """检查状态是否可以转换"""
    allowed = STATUS_FLOW.get(from_status, [])
    return to_status in allowed


def get_display_status(status: str) -> str:
    """获取状态的显示名称"""
    return STATUS_DISPLAY.get(status, status)
