"""
Ozon Products API endpoints.

Provides API endpoints for Ozon product management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.exceptions import OzonIntegrationError
from app.models.database import OzonProduct, Shop, TeamMember, User


router = APIRouter()


class OzonConnectionTestResponse(BaseModel):
    success: bool
    message: str


class OzonProductDbResponse(BaseModel):
    id: int
    shop_id: int
    ozon_product_id: str | None
    offer_id: str
    title: str | None

    class Config:
        from_attributes = True


class PaginatedOzonResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


class OzonSyncResponse(BaseModel):
    success: bool
    items_synced: int
    message: str


@router.get("/test-connection", response_model=OzonConnectionTestResponse)
async def test_ozon_connection(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test Ozon API connection."""
    pass


@router.get("/health")
async def ozon_health_check(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check Ozon integration health."""
    pass


@router.get("/db/products", response_model=PaginatedOzonResponse)
async def list_db_products(
    shop_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List products from database."""
    pass


@router.get("/db/products/{product_id}", response_model=OzonProductDbResponse)
async def get_db_product(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get product from database."""
    pass


@router.put("/db/products/{product_id}", response_model=OzonProductDbResponse)
async def update_db_product(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product in database."""
    pass


@router.post("/products/{product_id}/push", response_model=dict)
async def push_product_to_ozon(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Push product to Ozon."""
    pass


@router.post("/products/{product_id}/archive", response_model=dict)
async def archive_product(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Archive product on Ozon."""
    pass


@router.post("/products/{product_id}/unarchive", response_model=dict)
async def unarchive_product(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unarchive product on Ozon."""
    pass


@router.post("/products/images", response_model=dict)
async def upload_product_images(
    shop_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload product images to Ozon."""
    pass


@router.post("/sync/products", response_model=OzonSyncResponse)
async def sync_products(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync products from Ozon."""
    pass


@router.get("/db/stats")
async def get_db_stats(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get database statistics."""
    pass
