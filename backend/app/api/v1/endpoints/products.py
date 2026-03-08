import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import (
    PlatformProduct,
    Product,
    ProductVariant,
    Shop,
    TeamMember,
    User,
)

router = APIRouter()


class ProductVariantCreate(BaseModel):
    sku: str
    variant_attributes: Dict[str, Any] = {}
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    cost: Optional[float] = None
    barcode: Optional[str] = None


class ProductCreate(BaseModel):
    master_sku: str
    title: str
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    images: List[str] = []
    category_id: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, Any]] = None
    attributes: Dict[str, Any] = {}
    status: str = "active"
    tags: List[str] = []
    variants: List[ProductVariantCreate] = []


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    images: Optional[List[str]] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class PlatformProductInfo(BaseModel):
    platform: str
    platform_product_id: str
    platform_sku: Optional[str] = None
    platform_price: Optional[float] = None
    platform_currency: Optional[str] = None
    platform_stock: int = 0
    platform_status: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    master_sku: str
    title: str
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    images: List[str] = []
    category_id: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    status: str = "active"
    tags: List[str] = []
    platforms: List[PlatformProductInfo] = []
    created_at: str


class PaginatedResponse(BaseModel):
    data: List[ProductResponse]
    meta: Dict[str, Any]


@router.get("", response_model=PaginatedResponse)
async def get_products(
    platform: Optional[str] = None,
    shop_id: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[str] = None,
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

    query = select(Product).where(Product.team_id == member.team_id)

    if status:
        query = query.where(Product.status == status)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if q:
        query = query.where(Product.title.ilike(f"%{q}%"))

    count_query = select(Product).where(Product.team_id == member.team_id)
    if status:
        count_query = count_query.where(Product.status == status)
    if q:
        count_query = count_query.where(Product.title.ilike(f"%{q}%"))

    total_result = await db.execute(count_query)
    total = len(total_result.all())

    query = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(Product.created_at.desc())
    )
    result = await db.execute(query)
    products = result.scalars().all()

    product_responses = []
    for p in products:
        platform_query = select(PlatformProduct).where(
            PlatformProduct.product_id == p.id
        )
        if platform:
            platform_query = (
                platform_query.join(Product).join(Shop).where(Shop.platform == platform)
            )
        if shop_id:
            platform_query = platform_query.where(PlatformProduct.shop_id == shop_id)

        platform_result = await db.execute(platform_query)
        platform_products = platform_result.scalars().all()

        product_responses.append(
            ProductResponse(
                id=p.id,
                master_sku=p.master_sku,
                title=p.title,
                description=p.description,
                main_image_url=p.main_image_url,
                images=p.images,
                category_id=p.category_id,
                brand=p.brand,
                weight=p.weight,
                status=p.status,
                tags=p.tags,
                platforms=[
                    PlatformProductInfo(
                        platform=pp.shop.platform if pp.shop else "",
                        platform_product_id=pp.platform_product_id,
                        platform_sku=pp.platform_sku,
                        platform_price=pp.platform_price,
                        platform_currency=pp.platform_currency,
                        platform_stock=pp.platform_stock,
                        platform_status=pp.platform_status,
                    )
                    for pp in platform_products
                ],
                created_at=p.created_at.isoformat(),
            )
        )

    return PaginatedResponse(
        data=product_responses,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
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

    product = Product(
        id=str(uuid.uuid4()),
        team_id=member.team_id,
        master_sku=product_data.master_sku,
        title=product_data.title,
        description=product_data.description,
        main_image_url=product_data.main_image_url,
        images=product_data.images,
        category_id=product_data.category_id,
        brand=product_data.brand,
        weight=product_data.weight,
        dimensions=product_data.dimensions,
        attributes=product_data.attributes,
        status=product_data.status,
        tags=product_data.tags,
    )
    db.add(product)

    for variant_data in product_data.variants:
        variant = ProductVariant(
            id=str(uuid.uuid4()),
            product_id=product.id,
            sku=variant_data.sku,
            variant_attributes=variant_data.variant_attributes,
            price=variant_data.price,
            compare_at_price=variant_data.compare_at_price,
            cost=variant_data.cost,
            barcode=variant_data.barcode,
        )
        db.add(variant)

    await db.commit()
    await db.refresh(product)

    return ProductResponse(
        id=product.id,
        master_sku=product.master_sku,
        title=product.title,
        description=product.description,
        main_image_url=product.main_image_url,
        images=product.images,
        category_id=product.category_id,
        brand=product.brand,
        weight=product.weight,
        status=product.status,
        tags=product.tags,
        platforms=[],
        created_at=product.created_at.isoformat(),
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
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
        select(Product).where(
            and_(Product.id == product_id, Product.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = await db.execute(
        select(PlatformProduct).where(PlatformProduct.product_id == product.id)
    )
    platform_products = result.scalars().all()

    return ProductResponse(
        id=product.id,
        master_sku=product.master_sku,
        title=product.title,
        description=product.description,
        main_image_url=product.main_image_url,
        images=product.images,
        category_id=product.category_id,
        brand=product.brand,
        weight=product.weight,
        status=product.status,
        tags=product.tags,
        platforms=[
            PlatformProductInfo(
                platform=pp.shop.platform if pp.shop else "",
                platform_product_id=pp.platform_product_id,
                platform_sku=pp.platform_sku,
                platform_price=pp.platform_price,
                platform_currency=pp.platform_currency,
                platform_stock=pp.platform_stock,
                platform_status=pp.platform_status,
            )
            for pp in platform_products
        ],
        created_at=product.created_at.isoformat(),
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
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
        select(Product).where(
            and_(Product.id == product_id, Product.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.title is not None:
        product.title = product_data.title
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.main_image_url is not None:
        product.main_image_url = product_data.main_image_url
    if product_data.images is not None:
        product.images = product_data.images
    if product_data.category_id is not None:
        product.category_id = product_data.category_id
    if product_data.brand is not None:
        product.brand = product_data.brand
    if product_data.weight is not None:
        product.weight = product_data.weight
    if product_data.dimensions is not None:
        product.dimensions = product_data.dimensions
    if product_data.attributes is not None:
        product.attributes = product_data.attributes
    if product_data.status is not None:
        product.status = product_data.status
    if product_data.tags is not None:
        product.tags = product_data.tags

    await db.commit()
    await db.refresh(product)

    result = await db.execute(
        select(PlatformProduct).where(PlatformProduct.product_id == product.id)
    )
    platform_products = result.scalars().all()

    return ProductResponse(
        id=product.id,
        master_sku=product.master_sku,
        title=product.title,
        description=product.description,
        main_image_url=product.main_image_url,
        images=product.images,
        category_id=product.category_id,
        brand=product.brand,
        weight=product.weight,
        status=product.status,
        tags=product.tags,
        platforms=[
            PlatformProductInfo(
                platform=pp.shop.platform if pp.shop else "",
                platform_product_id=pp.platform_product_id,
                platform_sku=pp.platform_sku,
                platform_price=pp.platform_price,
                platform_currency=pp.platform_currency,
                platform_stock=pp.platform_stock,
                platform_status=pp.platform_status,
            )
            for pp in platform_products
        ],
        created_at=product.created_at.isoformat(),
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
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

    if member.role not in ["super_admin", "admin", "operator"]:
        raise HTTPException(status_code=403, detail="No permission to delete product")

    result = await db.execute(
        select(Product).where(
            and_(Product.id == product_id, Product.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()

    return {"success": True, "message": "Product deleted successfully"}
