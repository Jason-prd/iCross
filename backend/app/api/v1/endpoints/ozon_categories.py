"""
Ozon Categories API endpoints.

Provides API endpoints for Ozon category management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.exceptions import OzonIntegrationError
from app.models.database import (
    OzonCategoryTree,
    OzonCategoryAttribute,
    OzonAttributeValue,
    Shop,
    TeamMember,
    User,
)


router = APIRouter()


class OzonCategoryTreeResponse(BaseModel):
    id: int
    parent_id: int | None
    name: str
    children: list = []

    class Config:
        from_attributes = True


class OzonCategorySyncResponse(BaseModel):
    success: bool
    items_synced: int
    message: str


class OzonCategoryAttributeResponse(BaseModel):
    id: int
    category_id: int
    name: str
    type: str
    is_required: bool
    group_id: int | None
    dictionary_id: int | None
    max_value_count: int | None

    class Config:
        from_attributes = True


class OzonAttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str
    guid: str | None

    class Config:
        from_attributes = True


@router.get("/categories", response_model=list[OzonCategoryTreeResponse])
async def list_categories(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all categories for a shop."""
    pass


@router.post("/sync-category-tree", response_model=OzonCategorySyncResponse)
async def sync_category_tree(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync category tree from Ozon."""
    pass


@router.get("/category-tree", response_model=list[OzonCategoryTreeResponse])
async def get_category_tree(
    shop_id: int,
    parent_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category tree from database."""
    pass


@router.get("/category-tree/nested", response_model=list[dict])
async def get_nested_category_tree(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get nested category tree."""
    pass


@router.get("/category-tree/all", response_model=list[OzonCategoryTreeResponse])
async def get_all_category_tree(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all category tree."""
    pass


@router.get("/category-tree/{category_id}", response_model=OzonCategoryTreeResponse)
async def get_category_by_id(
    shop_id: int,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category by ID."""
    pass


@router.get(
    "/category-attributes/all", response_model=list[OzonCategoryAttributeResponse]
)
async def get_all_category_attributes(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all category attributes."""
    pass


@router.post("/sync-category-attributes", response_model=OzonCategorySyncResponse)
async def sync_category_attributes(
    shop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync category attributes from Ozon."""
    pass


@router.get("/category-attributes", response_model=list[OzonCategoryAttributeResponse])
async def get_category_attributes(
    shop_id: int,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category attributes."""
    pass


@router.get(
    "/category-attribute/values", response_model=list[OzonAttributeValueResponse]
)
async def get_attribute_values(
    shop_id: int,
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attribute values."""
    pass


@router.get("/category-attribute/values/remote", response_model=list[dict])
async def get_remote_attribute_values(
    shop_id: int,
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attribute values from Ozon API."""
    pass


@router.post("/description-category/tree", response_model=list[dict])
async def get_description_category_tree(
    shop_id: int,
    category_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get description category tree."""
    pass


@router.post("/description-category/attribute", response_model=list[dict])
async def get_description_category_attribute(
    shop_id: int,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get description category attribute."""
    pass


@router.post("/description-category/attribute/values", response_model=list[dict])
async def get_description_attribute_values(
    shop_id: int,
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get description attribute values."""
    pass


@router.post("/description-category/attribute/values/search", response_model=list[dict])
async def search_description_attribute_values(
    shop_id: int,
    category_id: int,
    attribute_id: int,
    keyword: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search description attribute values."""
    pass
