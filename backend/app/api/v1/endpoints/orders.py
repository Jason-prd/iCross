import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import (Order, OrderItem, OrderStatusHistory, Shop,
                                 TeamMember, User)

router = APIRouter()


class OrderItemResponse(BaseModel):
    model_config = {"extra": "allow"}

    id: str
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    title: str
    sku: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: str
    order_number: str
    platform: str
    shop_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    shipping_address: Dict[str, Any]
    currency: str
    subtotal_amount: float
    shipping_amount: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_status: str
    fulfillment_status: str
    shipping_carrier: Optional[str] = None
    shipping_tracking_number: Optional[str] = None
    status: str
    notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    items: List[OrderItemResponse] = []
    created_at: str
    updated_at: str


class ShippingInfo(BaseModel):
    carrier: str
    tracking_number: str
    shipped_at: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str
    shipping_info: Optional[ShippingInfo] = None
    notes: Optional[str] = None


class PaginatedResponse(BaseModel):
    data: List[OrderResponse]
    meta: Dict[str, Any]


@router.get("", response_model=PaginatedResponse)
async def get_orders(
    platform: Optional[str] = None,
    shop_id: Optional[str] = None,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    fulfillment_status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    customer_email: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    base_query = select(Order).where(Order.team_id == member.team_id)

    if platform:
        base_query = base_query.join(Shop, Order.shop_id == Shop.id).where(Shop.platform == platform)
    if shop_id:
        base_query = base_query.where(Order.shop_id == shop_id)
    if status:
        base_query = base_query.where(Order.status == status)
    if payment_status:
        base_query = base_query.where(Order.payment_status == payment_status)
    if fulfillment_status:
        base_query = base_query.where(Order.fulfillment_status == fulfillment_status)
    if customer_email:
        base_query = base_query.where(Order.customer_email == customer_email)
    if q:
        base_query = base_query.where(Order.order_number.ilike(f"%{q}%"))
    if start_date:
        base_query = base_query.where(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        base_query = base_query.where(Order.created_at <= datetime.fromisoformat(end_date))

    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0

    query = (
        base_query
        .options(selectinload(Order.shop))
        .offset((page - 1) * limit)
        .limit(limit)
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    order_ids = [o.id for o in orders]
    items_map = {}
    if order_ids:
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id.in_(order_ids))
        )
        all_items = items_result.scalars().all()
        for item in all_items:
            if item.order_id not in items_map:
                items_map[item.order_id] = []
            items_map[item.order_id].append(item)

    order_responses = []
    for o in orders:
        items = items_map.get(o.id, [])
        shop_platform = ""
        if o.shop:
            try:
                shop_platform = getattr(o.shop, 'platform', "") or ""
            except Exception:
                shop_platform = ""

        order_responses.append(
            OrderResponse(
                id=o.id,
                order_number=o.order_number,
                platform=shop_platform,
                shop_id=o.shop_id,
                customer_name=o.customer_name,
                customer_email=o.customer_email,
                customer_phone=o.customer_phone,
                shipping_address=o.shipping_address,
                currency=o.currency,
                subtotal_amount=float(o.subtotal_amount),
                shipping_amount=float(o.shipping_amount),
                tax_amount=float(o.tax_amount),
                discount_amount=float(o.discount_amount),
                total_amount=float(o.total_amount),
                payment_status=o.payment_status,
                fulfillment_status=o.fulfillment_status,
                shipping_carrier=o.shipping_carrier,
                shipping_tracking_number=o.shipping_tracking_number,
                status=o.status,
                notes=o.notes,
                extra_data=o.extra_data,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        product_id=item.product_id,
                        variant_id=item.variant_id,
                        title=item.title,
                        sku=item.sku,
                        quantity=item.quantity,
                        unit_price=float(item.unit_price),
                        subtotal=float(item.subtotal),
                    )
                    for item in items
                ],
                created_at=o.created_at.isoformat(),
                updated_at=o.updated_at.isoformat(),
            )
        )

    return PaginatedResponse(
        data=order_responses,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.shop))
        .where(and_(Order.id == order_id, Order.team_id == member.team_id))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    items = result.scalars().all()

    shop_platform = ""
    if order.shop:
        try:
            shop_platform = getattr(order.shop, 'platform', "") or ""
        except Exception:
            shop_platform = ""

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        platform=shop_platform,
        shop_id=order.shop_id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        currency=order.currency,
        subtotal_amount=float(order.subtotal_amount),
        shipping_amount=float(order.shipping_amount),
        tax_amount=float(order.tax_amount),
        discount_amount=float(order.discount_amount),
        total_amount=float(order.total_amount),
        payment_status=order.payment_status,
        fulfillment_status=order.fulfillment_status,
        shipping_carrier=order.shipping_carrier,
        shipping_tracking_number=order.shipping_tracking_number,
        status=order.status,
        notes=order.notes,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                title=item.title,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal),
            )
            for item in items
        ],
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
    )


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.shop))
        .where(and_(Order.id == order_id, Order.team_id == member.team_id))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_data.status

    if status_data.shipping_info:
        order.shipping_carrier = status_data.shipping_info.carrier
        order.shipping_tracking_number = status_data.shipping_info.tracking_number
        if status_data.shipping_info.shipped_at:
            order.shipped_at = datetime.fromisoformat(
                status_data.shipping_info.shipped_at
            )
        order.fulfillment_status = "fulfilled"

    if status_data.notes:
        order.notes = status_data.notes

    status_history = OrderStatusHistory(
        id=str(uuid.uuid4()),
        order_id=order.id,
        status=status_data.status,
        notes=status_data.notes,
        changed_by=current_user.id,
    )
    db.add(status_history)

    await db.commit()
    await db.refresh(order)

    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    items = result.scalars().all()

    shop_platform = ""
    if order.shop:
        try:
            shop_platform = getattr(order.shop, 'platform', "") or ""
        except Exception:
            shop_platform = ""

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        platform=shop_platform,
        shop_id=order.shop_id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        currency=order.currency,
        subtotal_amount=float(order.subtotal_amount),
        shipping_amount=float(order.shipping_amount),
        tax_amount=float(order.tax_amount),
        discount_amount=float(order.discount_amount),
        total_amount=float(order.total_amount),
        payment_status=order.payment_status,
        fulfillment_status=order.fulfillment_status,
        shipping_carrier=order.shipping_carrier,
        shipping_tracking_number=order.shipping_tracking_number,
        status=order.status,
        notes=order.notes,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                title=item.title,
                sku=item.sku,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal),
            )
            for item in items
        ],
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
    )
