# -*- coding: utf-8 -*-
"""
Dropship Orders API Endpoint - Sync Version
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.dropshipping import DropshipOrder, ProductSupplierLink
from app.models.database import Product, ProductVariant

router = APIRouter(tags=["Dropship Orders"])

# Use sync database
SYNC_DATABASE_URL = "sqlite:///./icross_dev.db"
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


def get_db():
    db = SyncSession()
    try:
        yield db
    finally:
        db.close()


# Schema
class DropshipOrderSchema(BaseModel):
    id: str
    platform_order_id: str
    sku: str
    quantity: int
    sale_price: float
    purchase_cost: float
    shipping_cost: float
    total_cost: float
    profit: float
    profit_rate: float
    status: str
    supplier_order_id: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DropshipStatsSchema(BaseModel):
    total: int
    pending: int
    processing: int
    shipped: int
    delivered: int
    total_profit: float


@router.get("", response_model=List[DropshipOrderSchema])
def get_dropship_orders(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    """Get dropship order list"""
    query = db.query(DropshipOrder)

    if status:
        query = query.filter(DropshipOrder.status == status)
    if search:
        query = query.filter(
            (DropshipOrder.platform_order_id.contains(search))
            | (DropshipOrder.sku.contains(search))
            | (DropshipOrder.tracking_number.contains(search))
        )

    return (
        query.order_by(DropshipOrder.created_at.desc()).offset(skip).limit(limit).all()
    )


@router.get("/stats", response_model=DropshipStatsSchema)
def get_dropship_stats(db: Session = Depends(get_db)):
    """Get dropship stats"""
    total = db.query(DropshipOrder).count()
    pending = db.query(DropshipOrder).filter(DropshipOrder.status == "pending").count()
    processing = (
        db.query(DropshipOrder).filter(DropshipOrder.status == "processing").count()
    )
    shipped = db.query(DropshipOrder).filter(DropshipOrder.status == "shipped").count()
    delivered = (
        db.query(DropshipOrder).filter(DropshipOrder.status == "delivered").count()
    )

    orders = db.query(DropshipOrder).all()
    total_profit = sum(o.profit for o in orders)

    return {
        "total": total,
        "pending": pending,
        "processing": processing,
        "shipped": shipped,
        "delivered": delivered,
        "total_profit": total_profit,
    }


@router.get("/{order_id}", response_model=DropshipOrderSchema)
def get_dropship_order(order_id: str, db: Session = Depends(get_db)):
    """Get dropship order detail"""
    order = db.query(DropshipOrder).filter(DropshipOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@router.post("/create")
def create_dropship_order(
    platform_order_id: str,
    sku: str,
    quantity: int = 1,
    sale_price: float = 0,
    db: Session = Depends(get_db),
):
    """Create dropship order"""
    variant = db.query(ProductVariant).filter(ProductVariant.sku == sku).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Product not found")

    spu = sku.split("-")[0] if "-" in sku else sku
    supplier_link = (
        db.query(ProductSupplierLink)
        .filter(ProductSupplierLink.spu == spu, ProductSupplierLink.is_active == True)
        .first()
    )

    if not supplier_link:
        raise HTTPException(status_code=404, detail="Supplier not found")

    purchase_cost = supplier_link.purchase_cost or 0
    shipping_cost = supplier_link.shipping_cost or 0
    total_cost = (purchase_cost + shipping_cost) * quantity
    profit = sale_price - total_cost
    profit_rate = (profit / sale_price * 100) if sale_price > 0 else 0

    order = DropshipOrder(
        id=f"do-{datetime.now().strftime('%Y%m%d%H%M%S')}-{quantity}",
        team_id="default-team",
        platform_order_id=platform_order_id,
        sku=sku,
        quantity=quantity,
        sale_price=sale_price,
        purchase_cost=purchase_cost,
        shipping_cost=shipping_cost,
        total_cost=total_cost,
        profit=profit,
        profit_rate=profit_rate,
        status="pending",
        order_placed_at=datetime.now(),
    )

    db.add(order)
    db.commit()

    return {"success": True, "order_id": order.id}


@router.post("/{order_id}/process")
def process_dropship_order(order_id: str, db: Session = Depends(get_db)):
    """Process dropship order"""
    order = db.query(DropshipOrder).filter(DropshipOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order status is not pending")

    order.status = "processing"
    order.supplier_order_at = datetime.now()
    order.supplier_order_id = f"1688-{order_id}"
    db.commit()

    return {"success": True, "message": "Dropship order created"}


@router.post("/{order_id}/ship")
def ship_dropship_order(
    order_id: str, tracking_number: str, carrier: str, db: Session = Depends(get_db)
):
    """Ship dropship order"""
    order = db.query(DropshipOrder).filter(DropshipOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "shipped"
    order.tracking_number = tracking_number
    order.shipping_carrier = carrier
    order.shipped_at = datetime.now()
    db.commit()

    return {"success": True, "message": "Order shipped"}
