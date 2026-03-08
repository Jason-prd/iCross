# -*- coding: utf-8 -*-
"""
选品管理API端点 - 同步版本
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Product

router = APIRouter(tags=["选品管理"])

# 使用同步数据库
SYNC_DATABASE_URL = "sqlite:///./icross_dev.db"
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


def get_db():
    """同步数据库会话"""
    db = SyncSession()
    try:
        yield db
    finally:
        db.close()


# Schema
class SelectionProductSchema(BaseModel):
    id: str
    master_sku: str
    title: str
    selection_status: str
    listing_status: str
    source_url: Optional[str] = None
    source_price: Optional[float] = None
    source_supplier: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SelectionStatsSchema(BaseModel):
    total: int
    selected: int
    pending: int
    listed: int


@router.get("", response_model=List[SelectionProductSchema])
def get_selection_products(
    selection_status: Optional[str] = Query(None),
    listing_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """获取选品商品列表"""
    query = db.query(Product)
    
    if selection_status:
        query = query.filter(Product.selection_status == selection_status)
    if listing_status:
        query = query.filter(Product.listing_status == listing_status)
    if search:
        query = query.filter(
            (Product.master_sku.contains(search)) | 
            (Product.title.contains(search))
        )
    
    return query.offset(skip).limit(limit).all()


@router.get("/stats", response_model=SelectionStatsSchema)
def get_selection_stats(db: Session = Depends(get_db)):
    """获取选品统计"""
    total = db.query(Product).count()
    selected = db.query(Product).filter(
        Product.selection_status == "selected"
    ).count()
    pending = db.query(Product).filter(
        Product.listing_status == "pending"
    ).count()
    listed = db.query(Product).filter(
        Product.listing_status == "listed"
    ).count()
    
    return {
        "total": total,
        "selected": selected,
        "pending": pending,
        "listed": listed
    }


@router.get("/{product_id}", response_model=SelectionProductSchema)
def get_selection_product(product_id: str, db: Session = Depends(get_db)):
    """获取单个选品商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return product


@router.post("/{product_id}/list")
def list_product(product_id: str, db: Session = Depends(get_db)):
    """上架商品到Ozon"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # TODO: 调用Ozon API上架
    product.listing_status = "listed"
    db.commit()
    
    return {"success": True, "message": "商品已上架"}
