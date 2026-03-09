# -*- coding: utf-8 -*-
"""
Selection Management API Endpoint - Sync Version
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Product

router = APIRouter(tags=["Selection Management"])

# Use sync database
SYNC_DATABASE_URL = "sqlite:///./icross_dev.db"
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


def get_db():
    """Sync database session"""
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
    db: Session = Depends(get_db),
):
    """Get selection product list"""
    query = db.query(Product)

    if selection_status:
        query = query.filter(Product.selection_status == selection_status)
    if listing_status:
        query = query.filter(Product.listing_status == listing_status)
    if search:
        query = query.filter(
            (Product.master_sku.contains(search)) | (Product.title.contains(search))
        )

    return query.offset(skip).limit(limit).all()


@router.get("/stats", response_model=SelectionStatsSchema)
def get_selection_stats(db: Session = Depends(get_db)):
    """Get selection stats"""
    total = db.query(Product).count()
    selected = db.query(Product).filter(Product.selection_status == "selected").count()
    pending = db.query(Product).filter(Product.listing_status == "pending").count()
    listed = db.query(Product).filter(Product.listing_status == "listed").count()

    return {"total": total, "selected": selected, "pending": pending, "listed": listed}


@router.get("/{product_id}", response_model=SelectionProductSchema)
def get_selection_product(product_id: str, db: Session = Depends(get_db)):
    """Get single selection product detail"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/{product_id}/list")
def list_product(product_id: str, db: Session = Depends(get_db)):
    """List product on Ozon"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # TODO: Call Ozon API to list
    product.listing_status = "listed"
    db.commit()

    return {"success": True, "message": "Product listed"}
