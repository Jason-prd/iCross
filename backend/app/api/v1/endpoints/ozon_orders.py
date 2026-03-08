"""
Ozon Orders API endpoints.

Provides API endpoints for Ozon order management.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import Shop, User


router = APIRouter()


class OzonOrderSyncResponse(BaseModel):
    success: bool
    orders_synced: int
    message: str


@router.post("/sync/orders", response_model=OzonOrderSyncResponse)
async def sync_orders(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync orders from Ozon."""
    pass


@router.get("/orders/fbo/{posting_number}", response_model=dict)
async def get_fbo_order(
    shop_id: int,
    posting_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get FBO order by posting number."""
    pass


@router.get("/orders/fbs/{posting_number}", response_model=dict)
async def get_fbs_order(
    shop_id: int,
    posting_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get FBS order by posting number."""
    pass


@router.get("/orders/unfulfilled", response_model=list[dict])
async def get_unfulfilled_orders(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get unfulfilled orders."""
    pass
