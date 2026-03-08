# -*- coding: utf-8 -*-
"""
运营仪表盘API端点 - 同步版本
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List

from app.models.database import Product, PlatformProduct

router = APIRouter(tags=["运营仪表盘"])

# 使用同步数据库
SYNC_DATABASE_URL = "sqlite:///./icross_dev.db"
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


def get_db():
    db = SyncSession()
    try:
        yield db
    finally:
        db.close()


class DashboardStats(BaseModel):
    selection_total: int
    selection_selected: int
    selection_pending: int
    selection_listed: int
    order_total: int
    order_pending: int
    order_processing: int
    order_completed: int
    order_total_amount: float
    dropship_total: int
    dropship_pending: int
    dropship_shipped: int
    dropship_total_profit: float
    product_total: int
    product_low_stock: int
    product_avg_profit_rate: float


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取运营仪表盘统计数据"""
    # 选品统计
    selection_total = db.query(Product).count()
    selection_selected = db.query(Product).filter(
        Product.selection_status == "selected"
    ).count()
    selection_pending = db.query(Product).filter(
        Product.listing_status == "pending"
    ).count()
    selection_listed = db.query(Product).filter(
        Product.listing_status == "listed"
    ).count()
    
    # 商品统计
    product_total = db.query(PlatformProduct).count()
    product_low_stock = db.query(PlatformProduct).filter(
        PlatformProduct.platform_stock < 10
    ).count()
    
    return {
        "selection_total": selection_total,
        "selection_selected": selection_selected,
        "selection_pending": selection_pending,
        "selection_listed": selection_listed,
        "order_total": 0,
        "order_pending": 0,
        "order_processing": 0,
        "order_completed": 0,
        "order_total_amount": 0,
        "dropship_total": 0,
        "dropship_pending": 0,
        "dropship_shipped": 0,
        "dropship_total_profit": 0,
        "product_total": product_total,
        "product_low_stock": product_low_stock,
        "product_avg_profit_rate": 28.5,
    }


@router.get("/low-stock")
def get_low_stock_products(limit: int = 10, db: Session = Depends(get_db)):
    """获取低库存商品"""
    products = db.query(PlatformProduct).filter(
        PlatformProduct.platform_stock < 10
    ).limit(limit).all()
    
    result = []
    for p in products:
        result.append({
            "sku": p.platform_sku,
            "name": p.platform_title or "",
            "stock": p.platform_stock,
            "threshold": 10
        })
    
    return result


@router.get("/recent-orders")
def get_recent_orders(limit: int = 5, db: Session = Depends(get_db)):
    """获取最近订单"""
    # 暂时返回空列表
    return []
