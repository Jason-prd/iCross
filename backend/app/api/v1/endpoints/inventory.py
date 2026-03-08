import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import (
    Inventory,
    InventoryAlert,
    InventoryTransaction,
    Product,
    TeamMember,
    User,
    Warehouse,
)

router = APIRouter()


class WarehouseResponse(BaseModel):
    id: str
    name: str
    code: str
    type: str = "physical"
    address: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    capacity: Optional[int] = None
    status: str = "active"


class InventoryItemResponse(BaseModel):
    product_id: str
    product_title: str
    product_sku: str
    variant_id: Optional[str] = None
    warehouses: List[Dict[str, Any]]
    total_quantity: int
    total_reserved: int
    total_available: int
    is_low_stock: bool


class InventoryAdjustmentRequest(BaseModel):
    product_id: str
    warehouse_id: str
    adjustment_type: str
    quantity_change: int
    reason: Optional[str] = None
    reference_number: Optional[str] = None


class InventoryAdjustmentResponse(BaseModel):
    adjustment_id: str
    product_id: str
    warehouse_id: str
    previous_quantity: int
    new_quantity: int
    adjustment_type: str
    adjusted_at: str


class PaginatedResponse(BaseModel):
    data: List[InventoryItemResponse]
    meta: Dict[str, Any]


@router.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
        select(Warehouse).where(
            and_(Warehouse.team_id == member.team_id, Warehouse.status == "active")
        )
    )
    warehouses = result.scalars().all()

    return [
        WarehouseResponse(
            id=w.id,
            name=w.name,
            code=w.code,
            type=w.type,
            address=w.address,
            contact_info=w.contact_info,
            capacity=w.capacity,
            status=w.status,
        )
        for w in warehouses
    ]


@router.post("/warehouses", response_model=WarehouseResponse)
async def create_warehouse(
    warehouse_data: dict,
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

    if member.role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="No permission to create warehouse")

    warehouse = Warehouse(
        id=str(uuid.uuid4()),
        team_id=member.team_id,
        name=warehouse_data.get("name"),
        code=warehouse_data.get("code"),
        type=warehouse_data.get("type", "physical"),
        address=warehouse_data.get("address"),
        contact_info=warehouse_data.get("contact_info"),
        capacity=warehouse_data.get("capacity"),
    )
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)

    return WarehouseResponse(
        id=warehouse.id,
        name=warehouse.name,
        code=warehouse.code,
        type=warehouse.type,
        address=warehouse.address,
        contact_info=warehouse.contact_info,
        capacity=warehouse.capacity,
        status=warehouse.status,
    )


@router.get("", response_model=PaginatedResponse)
async def get_inventory(
    product_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    low_stock: Optional[bool] = False,
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

    query = select(Inventory).where(Inventory.team_id == member.team_id)

    if product_id:
        query = query.where(Inventory.product_id == product_id)
    if warehouse_id:
        query = query.where(Inventory.warehouse_id == warehouse_id)

    result = await db.execute(query)
    inventory_items = result.scalars().all()

    inventory_by_product = {}
    for inv in inventory_items:
        if inv.product_id not in inventory_by_product:
            result = await db.execute(
                select(Product).where(Product.id == inv.product_id)
            )
            product = result.scalar_one_or_none()
            if not product:
                continue

            result = await db.execute(
                select(Warehouse).where(Warehouse.id == inv.warehouse_id)
            )
            warehouse = result.scalar_one_or_none()

            inventory_by_product[inv.product_id] = {
                "product_id": inv.product_id,
                "product_title": product.title if product else "",
                "product_sku": product.master_sku if product else "",
                "variant_id": inv.variant_id,
                "warehouses": [],
                "total_quantity": 0,
                "total_reserved": 0,
                "total_available": 0,
                "is_low_stock": False,
            }

        result = await db.execute(
            select(Warehouse).where(Warehouse.id == inv.warehouse_id)
        )
        warehouse = result.scalar_one_or_none()

        is_low = inv.quantity <= inv.safety_stock
        inventory_by_product[inv.product_id]["warehouses"].append(
            {
                "warehouse_id": inv.warehouse_id,
                "warehouse_name": warehouse.name if warehouse else "",
                "quantity": inv.quantity,
                "reserved_quantity": inv.reserved_quantity,
                "available_quantity": inv.quantity - inv.reserved_quantity,
                "safety_stock": inv.safety_stock,
                "last_updated": (
                    inv.last_updated_at.isoformat() if inv.last_updated_at else None
                ),
            }
        )
        inventory_by_product[inv.product_id]["total_quantity"] += inv.quantity
        inventory_by_product[inv.product_id]["total_reserved"] += inv.reserved_quantity
        if is_low:
            inventory_by_product[inv.product_id]["is_low_stock"] = True

    data = list(inventory_by_product.values())

    if low_stock:
        data = [d for d in data if d["is_low_stock"]]

    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    data = data[start:end]

    return PaginatedResponse(
        data=data,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if limit else 1,
        },
    )


@router.post("/adjust", response_model=InventoryAdjustmentResponse)
async def adjust_inventory(
    adjustment_data: InventoryAdjustmentRequest,
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
        select(Inventory).where(
            and_(
                Inventory.product_id == adjustment_data.product_id,
                Inventory.warehouse_id == adjustment_data.warehouse_id,
                Inventory.team_id == member.team_id,
            )
        )
    )
    inventory = result.scalar_one_or_none()

    if not inventory:
        inventory = Inventory(
            id=str(uuid.uuid4()),
            team_id=member.team_id,
            product_id=adjustment_data.product_id,
            warehouse_id=adjustment_data.warehouse_id,
            quantity=0,
            reserved_quantity=0,
        )
        db.add(inventory)
        await db.flush()

    previous_quantity = inventory.quantity
    inventory.quantity += adjustment_data.quantity_change
    if inventory.quantity < 0:
        raise HTTPException(status_code=400, detail="Inventory cannot be negative")

    transaction = InventoryTransaction(
        id=str(uuid.uuid4()),
        team_id=member.team_id,
        product_id=adjustment_data.product_id,
        variant_id=inventory.variant_id,
        warehouse_id=adjustment_data.warehouse_id,
        inventory_id=inventory.id,
        transaction_type=adjustment_data.adjustment_type,
        quantity_change=adjustment_data.quantity_change,
        previous_quantity=previous_quantity,
        new_quantity=inventory.quantity,
        reference_type=adjustment_data.reference_number,
        notes=adjustment_data.reason,
        created_by=current_user.id,
    )
    db.add(transaction)
    await db.commit()

    return InventoryAdjustmentResponse(
        adjustment_id=transaction.id,
        product_id=adjustment_data.product_id,
        warehouse_id=adjustment_data.warehouse_id,
        previous_quantity=previous_quantity,
        new_quantity=inventory.quantity,
        adjustment_type=adjustment_data.adjustment_type,
        adjusted_at=transaction.created_at.isoformat(),
    )


@router.get("/alerts")
async def get_inventory_alerts(
    acknowledged: Optional[bool] = None,
    resolved: Optional[bool] = None,
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

    query = select(InventoryAlert).where(InventoryAlert.team_id == member.team_id)

    if acknowledged is not None:
        query = query.where(InventoryAlert.acknowledged == acknowledged)
    if resolved is not None:
        query = query.where(InventoryAlert.resolved == resolved)

    result = await db.execute(query.order_by(InventoryAlert.triggered_at.desc()))
    alerts = result.scalars().all()

    return {"success": True, "data": alerts}
