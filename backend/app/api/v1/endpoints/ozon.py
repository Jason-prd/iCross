"""
Ozon Platform Integration API Endpoints

Provides REST API interfaces for Ozon platform integration.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.exceptions import OzonIntegrationError
from app.integrations.ozon.models import OzonProduct as OzonProductIntegration
from app.models.database import (
    OzonProduct,
    Shop,
    TeamMember,
    User,
    OzonCategoryTree,
    OzonCategoryAttribute,
    OzonAttributeValue,
)


def convert_db_to_integration_product(
    db_product: OzonProduct,
) -> OzonProductIntegration:
    """Convert database Ozon product model to integration model"""
    import json

    image_list = []
    images_data = db_product.images
    if isinstance(images_data, str):
        try:
            images_data = json.loads(images_data)
        except:
            images_data = []
    for img_url in images_data or []:
        if isinstance(img_url, str):
            image_list.append(img_url)
        elif isinstance(img_url, dict):
            image_list.append(img_url.get("url", ""))
        else:
            image_list.append(str(img_url))

    primary_image = db_product.primary_image or (image_list[0] if image_list else "")

    barcode_list = []
    barcodes_data = db_product.barcodes
    if isinstance(barcodes_data, str):
        try:
            barcodes_data = json.loads(barcodes_data)
        except:
            barcodes_data = []
    for bc in barcodes_data or []:
        if isinstance(bc, str):
            barcode_list.append(bc)
        else:
            barcode_list.append(str(bc))

    attrs_data = db_product.attributes
    if isinstance(attrs_data, str):
        try:
            attrs_data = json.loads(attrs_data)
        except:
            attrs_data = {}
    attrs = attrs_data or {}
    if not isinstance(attrs, list):
        attrs = []

    return OzonProductIntegration(
        product_id=db_product.ozon_product_id,
        offer_id=db_product.offer_id,
        name=db_product.title,
        sku=str(db_product.ozon_sku) if db_product.ozon_sku else db_product.offer_id,
        description=db_product.description,
        price=float(db_product.price) if db_product.price else 0.0,
        old_price=float(db_product.old_price) if db_product.old_price else None,
        marketing_price=float(db_product.marketing_price)
        if db_product.marketing_price
        else None,
        vat=db_product.vat,
        quantity=db_product.stock,
        visibility=db_product.visibility,
        category_id=db_product.category_id,
        type_id=db_product.type_id or db_product.category_id,
        brand=db_product.brand,
        barcode=barcode_list[0] if barcode_list else None,
        height=db_product.volume_weight,
        width=db_product.volume_weight,
        depth=db_product.volume_weight,
        dimension_unit="mm",
        weight=db_product.volume_weight,
        weight_unit="g",
        images=image_list,
        images360=[],
        color_image=primary_image,
        attributes=attrs,
        created_at=db_product.created_at,
        updated_at=db_product.updated_at,
        raw_data=db_product.extra_data or {},
    )


router = APIRouter(tags=["ozon"])


class OzonConnectionTestResponse(BaseModel):
    """Ozon connection test response"""

    connected: bool = Field(..., description="Connection status")
    message: str = Field(..., description="Message")
    categories_count: Optional[int] = Field(None, description="Categories count")
    products_count: Optional[int] = Field(None, description="Products count")


class OzonProductResponse(BaseModel):
    """Ozon product response"""

    product_id: Optional[int] = Field(None, description="Product ID")
    offer_id: str = Field(..., description="Offer ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Price")
    quantity: int = Field(..., description="Stock quantity")
    visibility: str = Field(..., description="Visibility")
    category_id: Optional[int] = Field(None, description="Category ID")


class OzonProductUpdateRequest(BaseModel):
    """Ozon product update request"""

    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    type_id: Optional[int] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    marketing_price: Optional[float] = None
    currency: Optional[str] = None
    stock: Optional[int] = None
    reserved_stock: Optional[int] = None
    stock_type: Optional[str] = None
    status: Optional[str] = None
    status_name: Optional[str] = None
    moderate_status: Optional[str] = None
    visibility: Optional[str] = None
    is_archived: Optional[bool] = None
    is_discounted: Optional[bool] = None
    is_super: Optional[bool] = None
    vat: Optional[str] = None
    commission_percent: Optional[float] = None
    volume_weight: Optional[float] = None
    barcodes: Optional[List[str]] = None
    images: Optional[List[str]] = None
    primary_image: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None
    platform_url: Optional[str] = None


class OzonProductDbResponse(BaseModel):
    """Ozon product database response"""

    id: str
    ozon_product_id: int
    ozon_sku: Optional[int] = None
    offer_id: str
    title: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    type_id: Optional[int] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    marketing_price: Optional[float] = None
    currency: Optional[str] = None
    stock: int = 0
    reserved_stock: int = 0
    stock_type: Optional[str] = None
    status: Optional[str] = None
    status_name: Optional[str] = None
    moderate_status: Optional[str] = None
    visibility: str = "INVISIBLE"
    is_archived: bool = False
    is_discounted: bool = False
    is_super: bool = False
    vat: Optional[str] = None
    commission_percent: Optional[float] = None
    volume_weight: Optional[float] = None
    barcodes: List[str] = []
    images: List[str] = []
    primary_image: Optional[str] = None
    attributes: Dict[str, Any] = {}
    extra_data: Dict[str, Any] = {}
    platform_url: Optional[str] = None
    last_synced_at: Optional[str] = None
    sync_status: str = "synced"
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class OzonCategoryResponse(BaseModel):
    """Ozon category response"""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    has_children: bool = Field(..., description="Has children")
    description: Optional[str] = Field(None, description="Category description")


class OzonSyncResponse(BaseModel):
    """Ozon sync response"""

    success: bool
    synced: int = 0
    updated: int = 0
    total: int = 0
    message: str


class PaginatedOzonResponse(BaseModel):
    """Ozon product paginated response"""

    data: List[OzonProductDbResponse]
    meta: Dict[str, Any]


@router.get("/test-connection", response_model=OzonConnectionTestResponse)
async def test_ozon_connection(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonConnectionTestResponse:
    """
    Test Ozon API connection

    Verify Ozon API credentials and connection status.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            success = await adapter.connect()

            return OzonConnectionTestResponse(
                connected=success,
                message="Connection successful" if success else "Connection failed",
                categories_count=None,
                products_count=None,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error: {str(e)}",
        )


@router.get("/categories", response_model=List[OzonCategoryResponse])
async def get_ozon_categories(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryResponse]:
    """
    Get Ozon category tree

    Get product category tree structure from Ozon platform.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            categories = await adapter.get_categories()

            result = []
            for cat in categories:
                cat_name = cat.name
                if not cat_name and cat.raw_data:
                    cat_name = cat.raw_data.get("category_name", "")

                cat_id = cat.id
                if not cat_id and cat.raw_data:
                    cat_id = cat.raw_data.get("description_category_id", 0)

                result.append(
                    OzonCategoryResponse(
                        id=cat_id,
                        name=cat_name,
                        parent_id=cat.parent_id,
                        has_children=cat.has_children,
                        description=cat.description,
                    )
                )

            return result

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Ozon categories: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error: {str(e)}",
        )


class OzonCategoryTreeResponse(BaseModel):
    """Ozon category tree response"""

    id: str
    description_category_id: int
    category_name: Optional[str] = None
    parent_id: Optional[int] = None
    type_id: Optional[int] = None
    type_name: Optional[str] = None
    disabled: bool = False
    children: List[Dict[str, Any]] = []
    last_synced_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class OzonCategoryAttributeResponse(BaseModel):
    """Ozon category attribute response"""

    id: str
    description_category_id: int
    type_id: int
    attribute_id: int
    attribute_name: Optional[str] = None
    attribute_description: Optional[str] = None
    attribute_type: Optional[str] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    is_required: bool = False
    is_aspect: bool = False
    is_collection: bool = False
    last_synced_at: Optional[str] = None

    class Config:
        from_attributes = True


class OzonAttributeValueResponse(BaseModel):
    """Ozon attribute value response"""

    id: str
    description_category_id: int
    type_id: int
    attribute_id: int
    value_id: int
    value: Optional[str] = None
    info: Optional[str] = None
    picture: Optional[str] = None
    last_synced_at: Optional[str] = None

    class Config:
        from_attributes = True


class OzonCategorySyncResponse(BaseModel):
    """Ozon category sync response"""

    success: bool
    categories_count: int = 0
    attributes_count: int = 0
    values_count: int = 0
    message: str
    languages: Optional[List[str]] = None


@router.post("/sync-category-tree", response_model=OzonCategorySyncResponse)
async def sync_ozon_category_tree(
    language: Optional[str] = Query(
        default="ZH_HANS", description="Language: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    sync_all: bool = Query(default=False, description="Whether to sync all languages"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategorySyncResponse:
    """
    Sync Ozon category tree to local database

    - language: Specify language (ZH_HANS/EN/RU)
    - sync_all: Whether to sync all three languages
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            languages_to_sync = ["ZH_HANS", "EN", "RU"] if sync_all else [language]
            total_categories = 0

            for lang in languages_to_sync:
                categories_data = await adapter.get_description_category_tree(
                    language=lang
                )

                for cat_data in categories_data:

                    async def process_category(
                        cat: Dict[str, Any],
                        parent_id: Optional[int] = None,
                        lang_code: str = "",
                    ):
                        nonlocal total_categories

                        desc_cat_id = cat.get("description_category_id")
                        if not desc_cat_id:
                            return

                        cat_name = cat.get("category_name", "")
                        type_id = cat.get("type_id")
                        type_name = cat.get("type_name", "")
                        disabled = cat.get("disabled", False)
                        children = cat.get("children", [])

                        existing = await db.execute(
                            select(OzonCategoryTree).where(
                                and_(
                                    OzonCategoryTree.team_id == member.team_id,
                                    OzonCategoryTree.description_category_id
                                    == desc_cat_id,
                                )
                            )
                        )
                        existing_cat = existing.scalar_one_or_none()

                        if existing_cat:
                            if lang_code == "ZH_HANS":
                                existing_cat.category_name = cat_name
                                existing_cat.type_name = type_name
                            elif lang_code == "EN":
                                existing_cat.category_name_en = cat_name
                                existing_cat.type_name_en = type_name
                            elif lang_code == "RU":
                                existing_cat.category_name_ru = cat_name
                                existing_cat.type_name_ru = type_name
                            existing_cat.type_id = type_id
                            existing_cat.disabled = disabled
                            existing_cat.children = children
                            existing_cat.raw_data = cat
                            existing_cat.last_synced_at = datetime.utcnow()
                        else:
                            new_cat = OzonCategoryTree(
                                team_id=member.team_id,
                                shop_id=shop.id,
                                description_category_id=desc_cat_id,
                                category_name=cat_name
                                if lang_code == "ZH_HANS"
                                else None,
                                category_name_en=cat_name
                                if lang_code == "EN"
                                else None,
                                category_name_ru=cat_name
                                if lang_code == "RU"
                                else None,
                                parent_id=parent_id,
                                type_id=type_id,
                                type_name=type_name if lang_code == "ZH_HANS" else None,
                                type_name_en=type_name if lang_code == "EN" else None,
                                type_name_ru=type_name if lang_code == "RU" else None,
                                disabled=disabled,
                                children=children,
                                raw_data=cat,
                                last_synced_at=datetime.utcnow(),
                            )
                            db.add(new_cat)

                        total_categories += 1

                        for child in children:
                            await process_category(child, desc_cat_id, lang_code)

                    await process_category(cat_data, lang_code=lang)

            await db.commit()

            return OzonCategorySyncResponse(
                success=True,
                categories_count=total_categories,
                message=f"Sync completed: {total_categories} categories ({', '.join(languages_to_sync)})",
                languages=languages_to_sync,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync category tree: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error: {str(e)}",
        )


@router.get("/category-tree", response_model=List[OzonCategoryTreeResponse])
async def get_ozon_category_tree(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    parent_id: Optional[int] = Query(default=None, description="Parent category ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryTreeResponse]:
    """
    Get locally stored Ozon category tree (flattened format)
    - Returns all top-level categories when parent_id is not provided
    - Returns direct child nodes when parent_id is provided
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryTree).where(OzonCategoryTree.team_id == member.team_id)
    )
    all_categories = result.scalars().all()

    if parent_id is not None:
        root_cats = [c for c in all_categories if c.parent_id == parent_id]
    else:
        root_cats = [c for c in all_categories if c.parent_id is None]

    return [
        OzonCategoryTreeResponse(
            id=c.id,
            description_category_id=c.description_category_id,
            category_name=c.category_name,
            parent_id=c.parent_id,
            type_id=c.type_id,
            type_name=c.type_name,
            disabled=c.disabled,
            children=c.children or [],
            last_synced_at=c.last_synced_at.isoformat() if c.last_synced_at else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in root_cats
    ]


@router.get("/category-tree/nested", response_model=List[dict])
async def get_ozon_category_tree_nested(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get locally stored Ozon category tree (nested 3-level structure)
    Format: Shoes > Sneakers and Athletic Shoes > Lifting Shoes/Curl Shoes
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryTree).where(OzonCategoryTree.team_id == member.team_id)
    )
    all_categories = result.scalars().all()

    def build_tree_node(cat) -> dict:
        """Recursively build tree node"""
        children_data = cat.children or []
        tree_children = []

        for child_data in children_data:
            child_desc_id = child_data.get("description_category_id")
            child_type_id = child_data.get("type_id")
            child_type_name = child_data.get("type_name")
            child_category_name = child_data.get("category_name")
            child_disabled = child_data.get("disabled", False)
            child_children = child_data.get("children", [])

            child_node = {
                "id": f"{cat.description_category_id}-{child_desc_id or child_type_id}",
                "description_category_id": child_desc_id,
                "category_name": child_category_name,
                "parent_id": cat.description_category_id,
                "type_id": child_type_id,
                "type_name": child_type_name,
                "disabled": child_disabled,
                "children": [],
                "last_synced_at": cat.last_synced_at.isoformat()
                if cat.last_synced_at
                else None,
                "created_at": cat.created_at.isoformat(),
                "updated_at": cat.updated_at.isoformat(),
            }

            if child_children:
                for grandchild_data in child_children:
                    grandchild_type_id = grandchild_data.get("type_id")
                    grandchild_type_name = grandchild_data.get("type_name")
                    grandchild_disabled = grandchild_data.get("disabled", False)

                    grandchild_node = {
                        "id": f"{child_desc_id or child_type_id}-{grandchild_type_id}",
                        "description_category_id": None,
                        "category_name": None,
                        "parent_id": child_type_id,
                        "type_id": grandchild_type_id,
                        "type_name": grandchild_type_name,
                        "disabled": grandchild_disabled,
                        "children": [],
                        "last_synced_at": cat.last_synced_at.isoformat()
                        if cat.last_synced_at
                        else None,
                        "created_at": cat.created_at.isoformat(),
                        "updated_at": cat.updated_at.isoformat(),
                    }
                    child_node["children"].append(grandchild_node)

            tree_children.append(child_node)

        return {
            "id": cat.id,
            "description_category_id": cat.description_category_id,
            "category_name": cat.category_name,
            "parent_id": cat.parent_id,
            "type_id": cat.type_id,
            "type_name": cat.type_name,
            "disabled": cat.disabled,
            "children": tree_children,
            "last_synced_at": cat.last_synced_at.isoformat()
            if cat.last_synced_at
            else None,
            "created_at": cat.created_at.isoformat(),
            "updated_at": cat.updated_at.isoformat(),
        }

    root_cats = [c for c in all_categories if c.parent_id is None]
    return [build_tree_node(c) for c in root_cats]


@router.get("/category-tree/all", response_model=List[OzonCategoryTreeResponse])
async def get_all_ozon_category_tree(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryTreeResponse]:
    """
    Get all locally stored Ozon categories
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryTree).where(OzonCategoryTree.team_id == member.team_id)
    )
    categories = result.scalars().all()

    return [
        OzonCategoryTreeResponse(
            id=c.id,
            description_category_id=c.description_category_id,
            category_name=c.category_name,
            parent_id=c.parent_id,
            type_id=c.type_id,
            type_name=c.type_name,
            disabled=c.disabled,
            children=c.children or [],
            last_synced_at=c.last_synced_at.isoformat() if c.last_synced_at else None,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in categories
    ]


@router.get("/category-tree/{category_id}", response_model=OzonCategoryTreeResponse)
async def get_ozon_category_by_id(
    category_id: int,
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategoryTreeResponse:
    """
    Get locally stored Ozon category by ID
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryTree).where(
            and_(
                OzonCategoryTree.team_id == member.team_id,
                OzonCategoryTree.description_category_id == category_id,
            )
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category does not exist")

    return OzonCategoryTreeResponse(
        id=category.id,
        description_category_id=category.description_category_id,
        category_name=category.category_name,
        parent_id=category.parent_id,
        type_id=category.type_id,
        type_name=category.type_name,
        disabled=category.disabled,
        children=category.children or [],
        last_synced_at=category.last_synced_at.isoformat()
        if category.last_synced_at
        else None,
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
    )


@router.get(
    "/category-attributes/all", response_model=List[OzonCategoryAttributeResponse]
)
async def get_all_ozon_category_attributes(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryAttributeResponse]:
    """
    Get all locally stored Ozon category attributes
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryAttribute).where(
            OzonCategoryAttribute.team_id == member.team_id
        )
    )
    attributes = result.scalars().all()

    return [
        OzonCategoryAttributeResponse(
            id=a.id,
            description_category_id=a.description_category_id,
            type_id=a.type_id,
            attribute_id=a.attribute_id,
            attribute_name=a.attribute_name,
            attribute_description=a.attribute_description,
            attribute_type=a.attribute_type,
            group_id=a.group_id,
            group_name=a.group_name,
            is_required=a.is_required,
            is_aspect=a.is_aspect,
            is_collection=a.is_collection,
            last_synced_at=a.last_synced_at.isoformat() if a.last_synced_at else None,
        )
        for a in attributes
    ]


@router.post("/sync-category-attributes", response_model=OzonCategorySyncResponse)
async def sync_ozon_category_attributes(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="Language: ZH_HANS/EN/RU"
    ),
    sync_all: bool = Query(default=False, description="Whether to sync all languages"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategorySyncResponse:
    """
    Sync Ozon category attributes to local database
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            languages_to_sync = ["ZH_HANS", "EN", "RU"] if sync_all else [language]
            total_attributes = 0

            for lang in languages_to_sync:
                attributes_data = await adapter.get_category_attributes(
                    description_category_id, type_id, language=lang
                )

                for attr_data in attributes_data:
                    attr_id = attr_data.get("id")
                    if not attr_id:
                        continue

                    existing = await db.execute(
                        select(OzonCategoryAttribute).where(
                            and_(
                                OzonCategoryAttribute.team_id == member.team_id,
                                OzonCategoryAttribute.description_category_id
                                == description_category_id,
                                OzonCategoryAttribute.type_id == type_id,
                                OzonCategoryAttribute.attribute_id == attr_id,
                            )
                        )
                    )
                    existing_attr = existing.scalar_one_or_none()

                    attr_name = attr_data.get("name", "")
                    group_name = attr_data.get("group_name", "")

                    if existing_attr:
                        if lang == "ZH_HANS":
                            existing_attr.attribute_name = attr_name
                            existing_attr.group_name = group_name
                        elif lang == "EN":
                            existing_attr.attribute_name_en = attr_name
                            existing_attr.group_name_en = group_name
                        elif lang == "RU":
                            existing_attr.attribute_name_ru = attr_name
                            existing_attr.group_name_ru = group_name
                        existing_attr.attribute_description = attr_data.get(
                            "description", ""
                        )
                        existing_attr.attribute_type = attr_data.get("type", "")
                        existing_attr.group_id = attr_data.get("group_id")
                        existing_attr.dictionary_id = attr_data.get("dictionary_id")
                        existing_attr.is_required = attr_data.get("is_required", False)
                        existing_attr.is_aspect = attr_data.get("is_aspect", False)
                        existing_attr.is_collection = attr_data.get(
                            "is_collection", False
                        )
                        existing_attr.category_dependent = attr_data.get(
                            "category_dependent", False
                        )
                        existing_attr.max_value_count = attr_data.get("max_value_count")
                        existing_attr.raw_data = attr_data
                        existing_attr.last_synced_at = datetime.utcnow()
                    else:
                        new_attr = OzonCategoryAttribute(
                            team_id=member.team_id,
                            shop_id=shop.id,
                            description_category_id=description_category_id,
                            type_id=type_id,
                            attribute_id=attr_id,
                            attribute_name=attr_name if lang == "ZH_HANS" else None,
                            attribute_name_en=attr_name if lang == "EN" else None,
                            attribute_name_ru=attr_name if lang == "RU" else None,
                            attribute_description=attr_data.get("description", ""),
                            attribute_type=attr_data.get("type", ""),
                            group_id=attr_data.get("group_id"),
                            group_name=group_name if lang == "ZH_HANS" else None,
                            group_name_en=group_name if lang == "EN" else None,
                            group_name_ru=group_name if lang == "RU" else None,
                            dictionary_id=attr_data.get("dictionary_id"),
                            is_required=attr_data.get("is_required", False),
                            is_aspect=attr_data.get("is_aspect", False),
                            is_collection=attr_data.get("is_collection", False),
                            category_dependent=attr_data.get(
                                "category_dependent", False
                            ),
                            max_value_count=attr_data.get("max_value_count"),
                            raw_data=attr_data,
                            last_synced_at=datetime.utcnow(),
                        )
                        db.add(new_attr)

                    total_attributes += 1

            await db.commit()

            return OzonCategorySyncResponse(
                success=True,
                attributes_count=total_attributes,
                message=f"Sync completed: {total_attributes} attributes ({', '.join(languages_to_sync)})",
                languages=languages_to_sync,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync category attributes: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error: {str(e)}",
        )


@router.get("/category-attributes", response_model=List[OzonCategoryAttributeResponse])
async def get_ozon_category_attributes(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryAttributeResponse]:
    """
    Get locally stored Ozon category attributes
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonCategoryAttribute).where(
            and_(
                OzonCategoryAttribute.team_id == member.team_id,
                OzonCategoryAttribute.description_category_id
                == description_category_id,
                OzonCategoryAttribute.type_id == type_id,
            )
        )
    )
    attributes = result.scalars().all()

    return [
        OzonCategoryAttributeResponse(
            id=a.id,
            description_category_id=a.description_category_id,
            type_id=a.type_id,
            attribute_id=a.attribute_id,
            attribute_name=a.attribute_name,
            attribute_description=a.attribute_description,
            attribute_type=a.attribute_type,
            group_id=a.group_id,
            group_name=a.group_name,
            is_required=a.is_required,
            is_aspect=a.is_aspect,
            is_collection=a.is_collection,
            last_synced_at=a.last_synced_at.isoformat() if a.last_synced_at else None,
        )
        for a in attributes
    ]


@router.get(
    "/category-attribute/values", response_model=List[OzonAttributeValueResponse]
)
async def get_ozon_attribute_values(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    attribute_id: int = Query(..., description="Attribute ID"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonAttributeValueResponse]:
    """
    Get locally stored Ozon attribute values
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonAttributeValue).where(
            and_(
                OzonAttributeValue.team_id == member.team_id,
                OzonAttributeValue.description_category_id == description_category_id,
                OzonAttributeValue.type_id == type_id,
                OzonAttributeValue.attribute_id == attribute_id,
            )
        )
    )
    values = result.scalars().all()

    return [
        OzonAttributeValueResponse(
            id=v.id,
            description_category_id=v.description_category_id,
            type_id=v.type_id,
            attribute_id=v.attribute_id,
            value_id=v.value_id,
            value=v.value,
            info=v.info,
            picture=v.picture,
            last_synced_at=v.last_synced_at.isoformat() if v.last_synced_at else None,
        )
        for v in values
    ]


@router.get("/category-attribute/values/remote", response_model=List[dict])
async def get_ozon_attribute_values_remote(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    attribute_id: int = Query(..., description="Attribute ID"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get attribute values directly from Ozon API (not saved to local database)
    Used to get attribute options when editing products
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Ozon shop not found")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            values = await adapter.get_attribute_values(
                description_category_id=description_category_id,
                type_id=type_id,
                attribute_id=attribute_id,
            )
            return values
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute values: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting attribute values: {str(e)}",
        )


@router.post("/description-category/tree", response_model=List[dict])
async def get_description_category_tree(
    language: Optional[str] = Query(
        default="ZH_HANS", description="Language: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get category tree from Ozon API (descriptive categories)
    Returns all levels of categories and types
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Ozon shop not found")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            categories = await adapter.get_description_category_tree(language=language)
            return categories
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category tree: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting category tree: {str(e)}",
        )


@router.post("/description-category/attribute", response_model=List[dict])
async def get_description_category_attribute(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="Language: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get category attributes from Ozon API
    Returns all attributes of the category, including dictionary_id for multi-select fields
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Ozon shop not found")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            attributes = await adapter.get_description_category_attribute(
                description_category_id=description_category_id,
                type_id=type_id,
                language=language,
            )
            return attributes
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category attributes: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting category attributes: {str(e)}",
        )


@router.post("/description-category/attribute/values", response_model=List[dict])
async def get_description_category_attribute_values(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    attribute_id: int = Query(..., description="Attribute ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="Language: ZH_HANS/EN/RU"
    ),
    last_value_id: Optional[int] = Query(default=0, description="Pagination ID"),
    limit: Optional[int] = Query(default=2000, description="Limit of returned items"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get attribute option values from Ozon API
    Returns all optional values for an attribute, used for dropdown selection
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Ozon shop not found")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            values = await adapter.get_attribute_values(
                description_category_id=description_category_id,
                type_id=type_id,
                attribute_id=attribute_id,
                language=language,
            )
            return values
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attribute values: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting attribute values: {str(e)}",
        )


@router.post("/description-category/attribute/values/search", response_model=List[dict])
async def search_description_category_attribute_values(
    description_category_id: int = Query(..., description="Category ID"),
    type_id: int = Query(..., description="Type ID"),
    attribute_id: int = Query(..., description="Attribute ID"),
    value: str = Query(..., description="Search keyword (at least 2 characters)"),
    limit: Optional[int] = Query(default=100, description="Limit of returned items"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Search attribute option values
    Search optional values for an attribute by keyword
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="Ozon shop not found")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            from ozonapi.seller.schemas import (
                DescriptionCategoryAttributeValuesSearchRequest,
            )

            request = DescriptionCategoryAttributeValuesSearchRequest(
                description_category_id=description_category_id,
                type_id=type_id,
                attribute_id=attribute_id,
                value=value,
                limit=limit,
            )
            result = await adapter._api.description_category_attribute_values_search(
                request=request
            )

            values = []
            if hasattr(result, "result") and result.result:
                for item in result.result:
                    if hasattr(item, "model_dump"):
                        values.append(item.model_dump())
                    else:
                        values.append(dict(item))
            return values
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search attribute values: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching attribute values: {str(e)}",
        )


@router.get("/health")
async def ozon_health_check() -> Dict[str, Any]:
    """
    Ozon integration health check

    Check basic health status of Ozon integration module.
    """
    try:
        from app.integrations.ozon import __version__ as ozon_version

        return {
            "status": "healthy",
            "module": "ozon_integration",
            "version": ozon_version,
            "timestamp": "2026-02-18T00:00:00Z",
        }
    except ImportError as e:
        return {
            "status": "unhealthy",
            "error": f"Module import failed: {str(e)}",
            "timestamp": "2026-02-18T00:00:00Z",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": f"Health check failed: {str(e)}",
            "timestamp": "2026-02-18T00:00:00Z",
        }


@router.get("/db/products", response_model=PaginatedOzonResponse)
async def get_ozon_products_from_db(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    status_filter: Optional[str] = Query(default=None, description="Status filter"),
    visibility: Optional[str] = Query(default=None, description="Visibility filter"),
    sku: Optional[str] = Query(default=None, description="SKU filter"),
    offer_id: Optional[str] = Query(default=None, description="Offer ID filter"),
    category_id: Optional[int] = Query(default=None, description="Category ID filter"),
    q: Optional[str] = Query(default=None, description="Search keyword"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedOzonResponse:
    """
    Get Ozon product list from database

    Get Ozon products that have been synced to local database.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    query = select(OzonProduct).where(OzonProduct.team_id == member.team_id)

    if shop_id:
        query = query.where(OzonProduct.shop_id == shop_id)
    if status_filter:
        query = query.where(OzonProduct.status == status_filter)
    if visibility:
        query = query.where(OzonProduct.visibility == visibility)
    if sku:
        query = query.where(OzonProduct.ozon_sku.ilike(f"%{sku}%"))
    if offer_id:
        query = query.where(OzonProduct.offer_id.ilike(f"%{offer_id}%"))
    if category_id:
        query = query.where(OzonProduct.category_id == category_id)
    if q:
        query = query.where(OzonProduct.title.ilike(f"%{q}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(OzonProduct.updated_at.desc())
    )
    result = await db.execute(query)
    products = result.scalars().all()

    return PaginatedOzonResponse(
        data=[
            OzonProductDbResponse(
                id=p.id,
                ozon_product_id=p.ozon_product_id,
                ozon_sku=p.ozon_sku,
                offer_id=p.offer_id,
                title=p.title,
                description=p.description,
                brand=p.brand,
                category_id=p.category_id,
                category_name=p.category_name,
                type_id=p.type_id,
                price=p.price,
                old_price=p.old_price,
                marketing_price=p.marketing_price,
                currency=p.currency,
                stock=p.stock,
                reserved_stock=p.reserved_stock,
                stock_type=p.stock_type,
                status=p.status,
                status_name=p.status_name,
                moderate_status=p.moderate_status,
                visibility=p.visibility,
                is_archived=p.is_archived,
                is_discounted=p.is_discounted,
                is_super=p.is_super,
                vat=p.vat,
                commission_percent=p.commission_percent,
                volume_weight=p.volume_weight,
                barcodes=json.loads(p.barcodes)
                if isinstance(p.barcodes, str)
                else (p.barcodes or []),
                images=json.loads(p.images)
                if isinstance(p.images, str)
                else (p.images or []),
                primary_image=p.primary_image,
                attributes=json.loads(p.attributes)
                if isinstance(p.attributes, str)
                else (p.attributes or {}),
                extra_data=json.loads(p.extra_data)
                if isinstance(p.extra_data, str)
                else (p.extra_data or {}),
                platform_url=p.platform_url,
                last_synced_at=(
                    p.last_synced_at.isoformat() if p.last_synced_at else None
                ),
                sync_status=p.sync_status,
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat(),
            )
            for p in products
        ],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
        },
    )


@router.get("/db/products/{product_id}", response_model=OzonProductDbResponse)
async def get_ozon_product_detail(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonProductDbResponse:
    """
    Get Ozon product detail
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    return OzonProductDbResponse(
        id=product.id,
        ozon_product_id=product.ozon_product_id,
        ozon_sku=product.ozon_sku,
        offer_id=product.offer_id,
        title=product.title,
        description=product.description,
        brand=product.brand,
        category_id=product.category_id,
        category_name=product.category_name,
        type_id=product.type_id,
        price=product.price,
        old_price=product.old_price,
        marketing_price=product.marketing_price,
        currency=product.currency,
        stock=product.stock,
        reserved_stock=product.reserved_stock,
        stock_type=product.stock_type,
        status=product.status,
        status_name=product.status_name,
        moderate_status=product.moderate_status,
        visibility=product.visibility,
        is_archived=product.is_archived,
        is_discounted=product.is_discounted,
        is_super=product.is_super,
        vat=product.vat,
        commission_percent=product.commission_percent,
        volume_weight=product.volume_weight,
        barcodes=json.loads(product.barcodes)
        if isinstance(product.barcodes, str)
        else (product.barcodes or []),
        images=json.loads(product.images)
        if isinstance(product.images, str)
        else (product.images or []),
        primary_image=product.primary_image,
        attributes=json.loads(product.attributes)
        if isinstance(product.attributes, str)
        else (product.attributes or {}),
        extra_data=json.loads(product.extra_data)
        if isinstance(product.extra_data, str)
        else (product.extra_data or {}),
        platform_url=product.platform_url,
        last_synced_at=(
            product.last_synced_at.isoformat() if product.last_synced_at else None
        ),
        sync_status=product.sync_status,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat(),
    )


@router.put("/db/products/{product_id}", response_model=OzonProductDbResponse)
async def update_ozon_product(
    product_id: str,
    update_data: OzonProductUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonProductDbResponse:
    """
    Update Ozon product information

    Update Ozon product information in local database for frontend editing.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(product, key):
            setattr(product, key, value)

    product.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(product)

    return OzonProductDbResponse(
        id=product.id,
        ozon_product_id=product.ozon_product_id,
        ozon_sku=product.ozon_sku,
        offer_id=product.offer_id,
        title=product.title,
        description=product.description,
        brand=product.brand,
        category_id=product.category_id,
        category_name=product.category_name,
        type_id=product.type_id,
        price=product.price,
        old_price=product.old_price,
        marketing_price=product.marketing_price,
        currency=product.currency,
        stock=product.stock,
        reserved_stock=product.reserved_stock,
        stock_type=product.stock_type,
        status=product.status,
        status_name=product.status_name,
        moderate_status=product.moderate_status,
        visibility=product.visibility,
        is_archived=product.is_archived,
        is_discounted=product.is_discounted,
        is_super=product.is_super,
        vat=product.vat,
        commission_percent=product.commission_percent,
        volume_weight=product.volume_weight,
        barcodes=json.loads(product.barcodes)
        if isinstance(product.barcodes, str)
        else (product.barcodes or []),
        images=json.loads(product.images)
        if isinstance(product.images, str)
        else (product.images or []),
        primary_image=product.primary_image,
        attributes=json.loads(product.attributes)
        if isinstance(product.attributes, str)
        else (product.attributes or {}),
        extra_data=json.loads(product.extra_data)
        if isinstance(product.extra_data, str)
        else (product.extra_data or {}),
        platform_url=product.platform_url,
        last_synced_at=(
            product.last_synced_at.isoformat() if product.last_synced_at else None
        ),
        sync_status=product.sync_status,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat(),
    )


@router.post("/products/{product_id}/push", response_model=Dict[str, Any])
async def push_ozon_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Push local Ozon product changes to Ozon platform
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Related shop does not exist")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            ozon_product = convert_db_to_integration_product(product)
            result = await adapter.update_product(ozon_product)
            return {
                "success": True,
                "task_id": result.get("task_id"),
                "message": "Product pushed to Ozon",
            }
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Push failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Push error: {str(e)}",
        )


@router.post("/products/{product_id}/archive", response_model=Dict[str, Any])
async def archive_ozon_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Archive product on Ozon platform
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    if not product.ozon_product_id:
        raise HTTPException(
            status_code=400, detail="Product not linked to Ozon product ID"
        )

    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Related shop does not exist")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            result = await adapter.archive_product(product.ozon_product_id)
            product.is_archived = True
            product.updated_at = datetime.utcnow()
            await db.commit()
            return {"success": True, "message": "Product archived"}
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Archive failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Archive error: {str(e)}",
        )


@router.post("/products/{product_id}/unarchive", response_model=Dict[str, Any])
async def unarchive_ozon_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Unarchive product on Ozon platform
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    if not product.ozon_product_id:
        raise HTTPException(
            status_code=400, detail="Product not linked to Ozon product ID"
        )

    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Related shop does not exist")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="Shop missing Ozon API credentials")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            result = await adapter.unarchive_product(product.ozon_product_id)
            product.is_archived = False
            product.updated_at = datetime.utcnow()
            await db.commit()
            return {"success": True, "message": "Product unarchived"}
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unarchive failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unarchive error: {str(e)}",
        )


class OzonProductImageRequest(BaseModel):
    """Ozon product image request"""

    offer_id: str = Field(..., description="Product offer ID")
    images: List[str] = Field(..., description="Image URL list")


@router.post("/products/images", response_model=Dict[str, Any])
async def import_product_images(
    request: OzonProductImageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Import product images to Ozon

    Associate image URLs with Ozon product.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(Shop).where(
            and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
        )
    )
    shop = result.scalars().first()

    if not shop:
        raise HTTPException(
            status_code=404, detail="Ozon shop not found, please add Ozon shop first"
        )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            items = [{"offer_id": request.offer_id, "images": request.images}]

            result = await adapter.import_product_images(items)

            return {
                "success": True,
                "offer_id": request.offer_id,
                "result": result,
            }

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import images: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing images: {str(e)}",
        )


@router.post("/sync/products", response_model=OzonSyncResponse)
async def sync_ozon_products(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonSyncResponse:
    """
    Sync Ozon products to database

    Get product information from Ozon API and store to local database.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            sync_result = await adapter.sync_products_to_database(
                db=db, team_id=member.team_id, shop_id=shop.id
            )

            return OzonSyncResponse(success=True, **sync_result)

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync error: {str(e)}",
        )


@router.get("/db/stats")
async def get_ozon_products_stats(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get Ozon product statistics
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    query = select(OzonProduct).where(OzonProduct.team_id == member.team_id)

    if shop_id:
        query = query.where(OzonProduct.shop_id == shop_id)

    result = await db.execute(query)
    products = result.scalars().all()

    total_products = len(products)
    total_stock = sum(p.stock for p in products)
    visible_count = sum(1 for p in products if p.visibility == "VISIBLE")
    archived_count = sum(1 for p in products if p.is_archived)

    return {
        "total_products": total_products,
        "total_stock": total_stock,
        "visible_products": visible_count,
        "archived_products": archived_count,
        "invisible_products": total_products - visible_count - archived_count,
    }


class OzonOrderResponse(BaseModel):
    """Ozon order response"""

    order_id: str
    order_number: str
    status: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    total_amount: float
    currency: str = "RUB"
    created_at: str
    updated_at: Optional[str] = None
    items: List[Dict[str, Any]] = []
    shipping_address: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class OzonOrderSyncResponse(BaseModel):
    """Ozon order sync response"""

    success: bool
    synced: int = 0
    updated: int = 0
    total: int = 0
    message: str


@router.post("/sync/orders", response_model=OzonOrderSyncResponse)
async def sync_ozon_orders(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    days_back: int = Query(
        default=7, ge=1, le=30, description="Days to sync (default 7)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonOrderSyncResponse:
    """
    Sync Ozon orders to database

    Get order information from Ozon API and store to local database.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            sync_result = await adapter.sync_orders_to_database(
                db=db, team_id=member.team_id, shop_id=shop.id, days_back=days_back
            )

            return OzonOrderSyncResponse(
                success=True,
                synced=sync_result["synced"],
                updated=sync_result["updated"],
                total=sync_result["total"],
                message=sync_result["message"],
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync error: {str(e)}",
        )


@router.get("/orders/fbo/{posting_number}", response_model=Dict[str, Any])
async def get_fbo_order_detail(
    posting_number: str,
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get FBO order detail

    FBO (Fulfillment by Ozon) order detail.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="Shop missing Ozon API credentials"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            detail = await adapter.get_fbo_order_detail(posting_number)
            return detail

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FBO order detail: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting FBO order detail: {str(e)}",
        )


@router.get("/orders/fbs/{posting_number}", response_model=Dict[str, Any])
async def get_fbs_order_detail(
    posting_number: str,
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get FBS order detail

    FBS (Fulfillment by Seller) order detail.
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="Shop missing Ozon API credentials"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            detail = await adapter.get_fbs_order_detail(posting_number)
            return detail

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get FBS order detail: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting FBS order detail: {str(e)}",
        )


@router.get("/orders/unfulfilled", response_model=List[Dict[str, Any]])
async def get_unfulfilled_postings(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get pending shipment order list

    Get all incomplete orders (awaiting shipment).
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="Shop missing Ozon API credentials"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            postings = await adapter.get_unfulfilled_postings()
            return postings

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending orders: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting pending orders: {str(e)}",
        )


class OzonWarehouseResponse(BaseModel):
    """Ozon warehouse response"""

    warehouse_id: str
    name: str
    is_fbos: bool = False
    is_fbs: bool = False
    is_premium: bool = False
    type: Optional[str] = None
    address: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class OzonDeliveryMethodResponse(BaseModel):
    """Ozon delivery method response"""

    delivery_method_id: str
    name: str
    warehouse_id: str
    warehouse_name: Optional[str] = None
    price: float = 0

    class Config:
        from_attributes = True


class OzonSellerInfoResponse(BaseModel):
    """Ozon seller info response"""

    seller_id: int
    name: str
    company: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


@router.get("/warehouses", response_model=List[OzonWarehouseResponse])
async def get_ozon_warehouses(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonWarehouseResponse]:
    """
    Get Ozon warehouse list
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            warehouses = await adapter.get_warehouses()

            return [
                OzonWarehouseResponse(
                    warehouse_id=w.warehouse_id,
                    name=w.name,
                    is_fbos=w.is_fbos,
                    is_fbs=w.is_fbs,
                    is_premium=w.is_premium,
                    type=w.type,
                    address=w.address,
                )
                for w in warehouses
            ]

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get warehouses: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting warehouses: {str(e)}",
        )


@router.get("/delivery-methods", response_model=List[OzonDeliveryMethodResponse])
async def get_ozon_delivery_methods(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonDeliveryMethodResponse]:
    """
    Get Ozon delivery method list
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            methods = await adapter.get_delivery_methods()

            return [
                OzonDeliveryMethodResponse(
                    delivery_method_id=m.delivery_method_id,
                    name=m.name,
                    warehouse_id=m.warehouse_id,
                    warehouse_name=m.warehouse_name,
                    price=m.price,
                )
                for m in methods
            ]

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get delivery methods: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting delivery methods: {str(e)}",
        )


@router.get("/seller-info", response_model=OzonSellerInfoResponse)
async def get_ozon_seller_info(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonSellerInfoResponse:
    """
    Get Ozon seller info
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            seller_info = await adapter.get_seller_info()

            return OzonSellerInfoResponse(
                seller_id=seller_info.seller_id,
                name=seller_info.name,
                company=seller_info.company,
                manager_id=seller_info.manager_id,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get seller info: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting seller info: {str(e)}",
        )


class OzonPriceUpdateRequest(BaseModel):
    """Ozon price update request"""

    offer_id: str
    price: float
    old_price: Optional[float] = None
    marketing_price: Optional[float] = None


class OzonStockUpdateRequest(BaseModel):
    """Ozon stock update request"""

    offer_id: str
    stock: int
    warehouse_id: Optional[str] = None


@router.post("/products/prices", response_model=Dict[str, Any])
async def update_ozon_product_prices(
    items: List[OzonPriceUpdateRequest],
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Batch update Ozon product prices
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            items_data = []
            for item in items:
                item_dict = {"offer_id": item.offer_id, "price": item.price}
                if item.old_price:
                    item_dict["old_price"] = item.old_price
                if item.marketing_price:
                    item_dict["marketing_price"] = item.marketing_price
                items_data.append(item_dict)

            result = await adapter.update_product_prices(items_data)

            return {
                "success": True,
                "task_id": result.get("task_id"),
                "message": f"Successfully submitted {len(items)} product price updates",
            }

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prices: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating prices: {str(e)}",
        )


@router.post("/products/stocks", response_model=Dict[str, Any])
async def update_ozon_product_stocks(
    items: List[OzonStockUpdateRequest],
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Batch update Ozon product stocks
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            items_data = []
            for item in items:
                item_dict = {"offer_id": item.offer_id, "stock": item.stock}
                if item.warehouse_id:
                    item_dict["warehouse_id"] = item.warehouse_id
                items_data.append(item_dict)

            result = await adapter.update_product_stocks(items_data)

            return {
                "success": True,
                "task_id": result.get("task_id"),
                "message": f"Successfully submitted {len(items)} product stock updates",
            }

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update stocks: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating stocks: {str(e)}",
        )


@router.get("/products/prices", response_model=List[Dict[str, Any]])
async def get_ozon_product_prices(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    product_ids: Optional[str] = Query(
        default=None, description="Product ID list, comma separated"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get Ozon product price information
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            product_ids_list = None
            if product_ids:
                product_ids_list = [int(x) for x in product_ids.split(",")]

            prices = await adapter.get_product_prices(product_ids_list)

            return [
                {
                    "product_id": p.product_id,
                    "offer_id": p.offer_id,
                    "price": p.price,
                    "old_price": p.old_price,
                    "marketing_price": p.marketing_price,
                    "currency": p.currency,
                }
                for p in prices
            ]

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prices: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prices: {str(e)}",
        )


@router.get("/products/stocks", response_model=List[Dict[str, Any]])
async def get_ozon_product_stocks(
    shop_id: Optional[str] = Query(default=None, description="Shop ID"),
    product_ids: Optional[str] = Query(
        default=None, description="Product ID list, comma separated"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get Ozon product stock information
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    if shop_id:
        result = await db.execute(
            select(Shop).where(
                and_(
                    Shop.id == shop_id,
                    Shop.team_id == member.team_id,
                    Shop.platform == "ozon",
                )
            )
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise HTTPException(status_code=404, detail="Ozon shop does not exist")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404,
                detail="Ozon shop not found, please add Ozon shop first",
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400,
                detail="Shop missing Ozon API credentials, please check shop configuration",
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            product_ids_list = None
            if product_ids:
                product_ids_list = [int(x) for x in product_ids.split(",")]

            stocks = await adapter.get_product_stocks(product_ids_list)

            return [
                {
                    "product_id": s.product_id,
                    "offer_id": s.offer_id,
                    "stock": s.stock,
                    "reserved_stock": s.reserved_stock,
                    "warehouse_id": s.warehouse_id,
                    "stock_type": s.stock_type,
                }
                for s in stocks
            ]

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stocks: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stocks: {str(e)}",
        )
