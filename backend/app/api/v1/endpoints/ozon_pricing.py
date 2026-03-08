"""
Ozon Pricing and Stock API endpoints.

Provides API endpoints for Ozon pricing and inventory management.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import Shop, User


router = APIRouter()


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
    pass


@router.get("/delivery-methods", response_model=list[OzonDeliveryMethodResponse])
async def list_delivery_methods(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List delivery methods."""
    pass


@router.get("/seller-info", response_model=OzonSellerInfoResponse)
async def get_seller_info(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get seller information."""
    pass


@router.post("/products/prices", response_model=dict)
async def update_prices(
    shop_id: int,
    items: list,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product prices."""
    pass


@router.post("/products/stocks", response_model=dict)
async def update_stocks(
    shop_id: int,
    items: list,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product stocks."""
    pass


@router.get("/products/prices", response_model=list[dict])
async def get_prices(
    shop_id: int,
    offer_ids: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product prices."""
    pass


@router.get("/products/stocks", response_model=list[dict])
async def get_stocks(
    shop_id: int,
    offer_ids: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product stocks."""
    pass
