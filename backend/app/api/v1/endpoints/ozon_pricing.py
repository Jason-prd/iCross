"""
Ozon Pricing and Stock API endpoints.

Provides API endpoints for Ozon pricing and inventory management.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.exceptions import OzonIntegrationError
from app.models.database import Shop, TeamMember, User


router = APIRouter()


async def get_shop_and_adapter(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get shop and validate user has access"""
    result = await db.execute(
        select(TeamMember).where(TeamMember.user_id == current_user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(select(Shop).where(Shop.id == str(shop_id)))
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    api_credentials = shop.api_credentials or {}
    client_id = api_credentials.get("client_id")
    api_key = api_credentials.get("api_key")

    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
    await adapter.connect()

    return shop, adapter


class OzonWarehouseResponse(BaseModel):
    id: int
    name: str
    is_fbs: bool

    class Config:
        from_attributes = True


class OzonDeliveryMethodResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class OzonSellerInfoResponse(BaseModel):
    seller_id: int
    company_name: str

    class Config:
        from_attributes = True


@router.get("/warehouses", response_model=list[OzonWarehouseResponse])
async def list_warehouses(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List Ozon warehouses."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        warehouses = await adapter.get_warehouses()
        await adapter.disconnect()

        return [
            {"id": w.warehouse_id, "name": w.name, "is_fbs": w.is_fbs}
            for w in warehouses
        ]
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/delivery-methods", response_model=list[OzonDeliveryMethodResponse])
async def list_delivery_methods(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List delivery methods."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        methods = await adapter.get_delivery_methods()
        await adapter.disconnect()

        return [{"id": m.delivery_method_id, "name": m.name} for m in methods]
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/seller-info", response_model=OzonSellerInfoResponse)
async def get_seller_info(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get seller information."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        seller_info = await adapter.get_seller_info()
        await adapter.disconnect()

        return {
            "seller_id": seller_info.seller_id,
            "company_name": seller_info.company,
        }
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


class PriceUpdateItem(BaseModel):
    offer_id: str
    price: float
    old_price: Optional[float] = None


class StockUpdateItem(BaseModel):
    offer_id: str
    stock: int


@router.post("/products/prices", response_model=dict)
async def update_prices(
    shop_id: int,
    items: list[PriceUpdateItem],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product prices."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        items_dict = [
            {
                "offer_id": item.offer_id,
                "price": item.price,
                "old_price": item.old_price,
            }
            for item in items
        ]
        result = await adapter.update_product_prices(items_dict)
        await adapter.disconnect()

        return {"success": True, "result": result}
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/products/stocks", response_model=dict)
async def update_stocks(
    shop_id: int,
    items: list[StockUpdateItem],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product stocks."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        items_dict = [
            {"offer_id": item.offer_id, "stock": item.stock} for item in items
        ]
        result = await adapter.update_product_stocks(items_dict)
        await adapter.disconnect()

        return {"success": True, "result": result}
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/products/prices", response_model=list[dict])
async def get_prices(
    shop_id: int,
    offer_ids: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product prices."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        offer_id_list = [o.strip() for o in offer_ids.split(",") if o.strip()]
        product_ids: Optional[List[int]] = None
        prices = await adapter.get_product_prices(product_ids)
        await adapter.disconnect()

        return [
            {
                "offer_id": p.offer_id,
                "price": p.price,
                "old_price": p.old_price,
                "marketing_price": p.marketing_price,
            }
            for p in prices
        ]
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/products/stocks", response_model=list[dict])
async def get_stocks(
    shop_id: int,
    offer_ids: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product stocks."""
    try:
        shop, adapter = await get_shop_and_adapter(shop_id, db, current_user)
        offer_id_list = [o.strip() for o in offer_ids.split(",") if o.strip()]
        product_ids: Optional[List[int]] = None
        stocks = await adapter.get_product_stocks(product_ids)
        await adapter.disconnect()

        return [
            {
                "offer_id": s.offer_id,
                "stock": s.stock,
                "reserved": s.reserved_stock,
            }
            for s in stocks
        ]
    except OzonIntegrationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
