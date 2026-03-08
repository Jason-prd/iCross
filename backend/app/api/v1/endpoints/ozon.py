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
    """转换数据库Ozon商品模型为集成模型"""
    import json

    # 解析images - 可能存储为JSON字符串
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

    # 获取主图
    primary_image = db_product.primary_image or (image_list[0] if image_list else "")

    # 解析barcodes - 可能存储为JSON字符串
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

    # 解析attributes - 可能存储为JSON字符串
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
    """Ozon连接测试响应"""

    connected: bool = Field(..., description="连接状态")
    message: str = Field(..., description="消息")
    categories_count: Optional[int] = Field(None, description="分类数量")
    products_count: Optional[int] = Field(None, description="商品数量")


class OzonProductResponse(BaseModel):
    """Ozon商品响应"""

    product_id: Optional[int] = Field(None, description="商品ID")
    offer_id: str = Field(..., description="货号")
    name: str = Field(..., description="商品名称")
    price: float = Field(..., description="价格")
    quantity: int = Field(..., description="库存数量")
    visibility: str = Field(..., description="可见性")
    category_id: Optional[int] = Field(None, description="分类ID")


class OzonProductUpdateRequest(BaseModel):
    """Ozon商品更新请求"""

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
    """Ozon商品数据库响应"""

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
    """Ozon分类响应"""

    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    has_children: bool = Field(..., description="是否有子分类")
    description: Optional[str] = Field(None, description="分类描述")


class OzonSyncResponse(BaseModel):
    """Ozon同步响应"""

    success: bool
    synced: int = 0
    updated: int = 0
    total: int = 0
    message: str


class PaginatedOzonResponse(BaseModel):
    """Ozon商品分页响应"""

    data: List[OzonProductDbResponse]
    meta: Dict[str, Any]


@router.get("/test-connection", response_model=OzonConnectionTestResponse)
async def test_ozon_connection(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonConnectionTestResponse:
    """
    测试Ozon API连接

    验证Ozon API凭证和连接状态。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            success = await adapter.connect()

            return OzonConnectionTestResponse(
                connected=success,
                message="连接成功" if success else "连接失败",
                categories_count=None,
                products_count=None,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}",
        )


@router.get("/categories", response_model=List[OzonCategoryResponse])
async def get_ozon_categories(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryResponse]:
    """
    获取Ozon分类树

    获取Ozon平台的商品分类树结构。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            categories = await adapter.get_categories()

            result = []
            for cat in categories:
                # Try to get category name from different sources
                cat_name = cat.name
                if not cat_name and cat.raw_data:
                    cat_name = cat.raw_data.get("category_name", "")

                # Get description_category_id from raw_data
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
            detail=f"获取Ozon分类失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}",
        )


class OzonCategoryTreeResponse(BaseModel):
    """Ozon分类树响应"""

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
    """Ozon分类属性响应"""

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
    """Ozon属性值响应"""

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
    """Ozon分类同步响应"""

    success: bool
    categories_count: int = 0
    attributes_count: int = 0
    values_count: int = 0
    message: str
    languages: Optional[List[str]] = None


@router.post("/sync-category-tree", response_model=OzonCategorySyncResponse)
async def sync_ozon_category_tree(
    language: Optional[str] = Query(
        default="ZH_HANS", description="语言: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    sync_all: bool = Query(default=False, description="是否同步所有语言"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategorySyncResponse:
    """
    同步Ozon分类树到本地数据库

    - language: 指定语言 (ZH_HANS/EN/RU)
    - sync_all: 是否同步所有三种语言
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
                message=f"同步完成: 共{total_categories}个分类 ({', '.join(languages_to_sync)})",
                languages=languages_to_sync,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步分类树失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}",
        )


@router.get("/category-tree", response_model=List[OzonCategoryTreeResponse])
async def get_ozon_category_tree(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    parent_id: Optional[int] = Query(default=None, description="父分类ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryTreeResponse]:
    """
    获取本地存储的Ozon分类树（扁平格式）
    - 不传parent_id时返回所有一级分类
    - 传parent_id时返回该分类下的直接子节点
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 查询所有分类
    result = await db.execute(
        select(OzonCategoryTree).where(OzonCategoryTree.team_id == member.team_id)
    )
    all_categories = result.scalars().all()

    # 如果传了parent_id，查询该分类下的直接子节点
    if parent_id is not None:
        root_cats = [c for c in all_categories if c.parent_id == parent_id]
    else:
        # 否则查询一级分类（parent_id为None的）
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
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    获取本地存储的Ozon分类树（嵌套三层结构）
    返回格式：鞋类 > 运动鞋和工作鞋 > 举重鞋/冰壶鞋
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 查询所有分类
    result = await db.execute(
        select(OzonCategoryTree).where(OzonCategoryTree.team_id == member.team_id)
    )
    all_categories = result.scalars().all()

    def build_tree_node(cat) -> dict:
        """递归构建树节点"""
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

            # 递归处理三级节点
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

    # 查询一级分类
    root_cats = [c for c in all_categories if c.parent_id is None]
    return [build_tree_node(c) for c in root_cats]


@router.get("/category-tree/all", response_model=List[OzonCategoryTreeResponse])
async def get_all_ozon_category_tree(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryTreeResponse]:
    """
    获取所有本地存储的Ozon分类
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategoryTreeResponse:
    """
    根据分类ID获取本地存储的Ozon分类
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="分类不存在")

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
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryAttributeResponse]:
    """
    获取所有本地存储的Ozon分类属性
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="语言: ZH_HANS/EN/RU"
    ),
    sync_all: bool = Query(default=False, description="是否同步所有语言"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonCategorySyncResponse:
    """
    同步Ozon分类属性到本地数据库
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
                message=f"同步完成: 共{total_attributes}个属性 ({', '.join(languages_to_sync)})",
                languages=languages_to_sync,
            )

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步分类属性失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(e)}",
        )


@router.get("/category-attributes", response_model=List[OzonCategoryAttributeResponse])
async def get_ozon_category_attributes(
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonCategoryAttributeResponse]:
    """
    获取本地存储的Ozon分类属性
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    attribute_id: int = Query(..., description="属性ID"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonAttributeValueResponse]:
    """
    获取本地存储的Ozon属性值
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    attribute_id: int = Query(..., description="属性ID"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    直接从Ozon API获取属性值（不保存到本地数据库）
    用于商品编辑时获取属性选项
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="未找到Ozon店铺")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

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
            detail=f"获取属性值失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取属性值错误: {str(e)}",
        )


@router.post("/description-category/tree", response_model=List[dict])
async def get_description_category_tree(
    language: Optional[str] = Query(
        default="ZH_HANS", description="语言: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    从Ozon API获取分类树（描述性分类）
    返回所有层级的分类和类型
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="未找到Ozon店铺")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            categories = await adapter.get_description_category_tree(language=language)
            return categories
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类树失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类树错误: {str(e)}",
        )


@router.post("/description-category/attribute", response_model=List[dict])
async def get_description_category_attribute(
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="语言: ZH_HANS/EN/RU"
    ),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    从Ozon API获取分类属性
    返回分类的所有属性，包含多选字段的dictionary_id
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="未找到Ozon店铺")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

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
            detail=f"获取分类属性失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类属性错误: {str(e)}",
        )


@router.post("/description-category/attribute/values", response_model=List[dict])
async def get_description_category_attribute_values(
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    attribute_id: int = Query(..., description="属性ID"),
    language: Optional[str] = Query(
        default="ZH_HANS", description="语言: ZH_HANS/EN/RU"
    ),
    last_value_id: Optional[int] = Query(default=0, description="分页ID"),
    limit: Optional[int] = Query(default=2000, description="返回数量限制"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    从Ozon API获取属性选项值
    返回属性的所有可选值，用于下拉选择
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="未找到Ozon店铺")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

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
            detail=f"获取属性值失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取属性值错误: {str(e)}",
        )


@router.post("/description-category/attribute/values/search", response_model=List[dict])
async def search_description_category_attribute_values(
    description_category_id: int = Query(..., description="分类ID"),
    type_id: int = Query(..., description="类型ID"),
    attribute_id: int = Query(..., description="属性ID"),
    value: str = Query(..., description="搜索关键词（至少2个字符）"),
    limit: Optional[int] = Query(default=100, description="返回数量限制"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    搜索属性选项值
    根据关键词搜索属性的可选值
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
        raise HTTPException(status_code=404, detail="未找到Ozon店铺")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            # 直接调用API进行搜索
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
            detail=f"搜索属性值失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索属性值错误: {str(e)}",
        )


@router.get("/health")
async def ozon_health_check() -> Dict[str, Any]:
    """
    Ozon集成健康检查

    检查Ozon集成模块的基本健康状况。
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
            "error": f"模块导入失败: {str(e)}",
            "timestamp": "2026-02-18T00:00:00Z",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": f"健康检查失败: {str(e)}",
            "timestamp": "2026-02-18T00:00:00Z",
        }


@router.get("/db/products", response_model=PaginatedOzonResponse)
async def get_ozon_products_from_db(
    page: int = Query(default=1, ge=1, description="页码"),
    limit: int = Query(default=50, ge=1, le=100, description="每页数量"),
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    status_filter: Optional[str] = Query(default=None, description="状态筛选"),
    visibility: Optional[str] = Query(default=None, description="可见性筛选"),
    sku: Optional[str] = Query(default=None, description="SKU筛选"),
    offer_id: Optional[str] = Query(default=None, description="Offer ID筛选"),
    category_id: Optional[int] = Query(default=None, description="分类ID筛选"),
    q: Optional[str] = Query(default=None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedOzonResponse:
    """
    从数据库获取Ozon商品列表

    获取已同步到本地数据库的Ozon商品。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
                # Parse JSON strings back to lists
                barcodes=json.loads(p.barcodes)
                if isinstance(p.barcodes, str)
                else (p.barcodes or []),
                images=json.loads(p.images)
                if isinstance(p.images, str)
                else (p.images or []),
                primary_image=p.primary_image,
                # Parse JSON strings back to dicts
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
    获取Ozon商品详情
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

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
        # Parse JSON strings back to lists
        barcodes=json.loads(product.barcodes)
        if isinstance(product.barcodes, str)
        else (product.barcodes or []),
        images=json.loads(product.images)
        if isinstance(product.images, str)
        else (product.images or []),
        primary_image=product.primary_image,
        # Parse JSON strings back to dicts
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
    更新Ozon商品信息

    更新本地数据库中的Ozon商品信息，用于前端编辑。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 更新字段
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
        # Parse JSON strings back to lists
        barcodes=json.loads(product.barcodes)
        if isinstance(product.barcodes, str)
        else (product.barcodes or []),
        images=json.loads(product.images)
        if isinstance(product.images, str)
        else (product.images or []),
        primary_image=product.primary_image,
        # Parse JSON strings back to dicts
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
    将本地Ozon商品更改推送到Ozon平台
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 获取店铺凭证
    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="关联店铺不存在")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            # 转换商品模型
            ozon_product = convert_db_to_integration_product(product)
            result = await adapter.update_product(ozon_product)
            return {
                "success": True,
                "task_id": result.get("task_id"),
                "message": "商品已推送到Ozon",
            }
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推送失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推送错误: {str(e)}",
        )


@router.post("/products/{product_id}/archive", response_model=Dict[str, Any])
async def archive_ozon_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    在Ozon平台归档商品
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if not product.ozon_product_id:
        raise HTTPException(status_code=400, detail="商品未关联Ozon商品ID")

    # 获取店铺凭证
    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="关联店铺不存在")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            result = await adapter.archive_product(product.ozon_product_id)
            # 更新本地商品状态
            product.is_archived = True
            product.updated_at = datetime.utcnow()
            await db.commit()
            return {"success": True, "message": "商品已归档"}
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"归档失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"归档错误: {str(e)}",
        )


@router.post("/products/{product_id}/unarchive", response_model=Dict[str, Any])
async def unarchive_ozon_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    在Ozon平台取消归档商品
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    result = await db.execute(
        select(OzonProduct).where(
            and_(OzonProduct.id == product_id, OzonProduct.team_id == member.team_id)
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if not product.ozon_product_id:
        raise HTTPException(status_code=400, detail="商品未关联Ozon商品ID")

    # 获取店铺凭证
    result = await db.execute(
        select(Shop).where(
            and_(Shop.id == product.shop_id, Shop.team_id == member.team_id)
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="关联店铺不存在")

    client_id = shop.api_credentials.get("client_id")
    api_key = shop.api_credentials.get("api_key")
    if not client_id or not api_key:
        raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            result = await adapter.unarchive_product(product.ozon_product_id)
            # 更新本地商品状态
            product.is_archived = False
            product.updated_at = datetime.utcnow()
            await db.commit()
            return {"success": True, "message": "商品已取消归档"}
    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消归档失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消归档错误: {str(e)}",
        )


class OzonProductImageRequest(BaseModel):
    """Ozon商品图片请求"""

    offer_id: str = Field(..., description="商品货号")
    images: List[str] = Field(..., description="图片URL列表")


@router.post("/products/images", response_model=Dict[str, Any])
async def import_product_images(
    request: OzonProductImageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    导入商品图片到Ozon

    将图片URL关联到Ozon商品。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 获取用户的Ozon店铺
    result = await db.execute(
        select(Shop).where(
            and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
        )
    )
    shop = result.scalars().first()

    if not shop:
        raise HTTPException(status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺")

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            # 构建图片导入项
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
            detail=f"导入图片失败: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入图片错误: {str(e)}",
        )


@router.post("/sync/products", response_model=OzonSyncResponse)
async def sync_ozon_products(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonSyncResponse:
    """
    同步Ozon商品到数据库

    从Ozon API获取商品信息并存储到本地数据库。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"同步失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步错误: {str(e)}",
        )


@router.get("/db/stats")
async def get_ozon_products_stats(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    获取Ozon商品统计信息
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
    """Ozon订单响应"""

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
    """Ozon订单同步响应"""

    success: bool
    synced: int = 0
    updated: int = 0
    total: int = 0
    message: str


@router.post("/sync/orders", response_model=OzonOrderSyncResponse)
async def sync_ozon_orders(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    days_back: int = Query(default=7, ge=1, le=30, description="同步天数（默认7天）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonOrderSyncResponse:
    """
    同步Ozon订单到数据库

    从Ozon API获取订单信息并存储到本地数据库。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
            )

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            # 同步订单到数据库
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
            detail=f"同步失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步错误: {str(e)}",
        )


@router.get("/orders/fbo/{posting_number}", response_model=Dict[str, Any])
async def get_fbo_order_detail(
    posting_number: str,
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    获取FBO订单详情

    FBO (Fulfillment by Ozon) 订单详情。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 获取店铺
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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            detail = await adapter.get_fbo_order_detail(posting_number)
            return detail

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取FBO订单详情失败: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取FBO订单详情错误: {str(e)}",
        )


@router.get("/orders/fbs/{posting_number}", response_model=Dict[str, Any])
async def get_fbs_order_detail(
    posting_number: str,
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    获取FBS订单详情

    FBS (Fulfillment by Seller) 订单详情。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 获取店铺
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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            detail = await adapter.get_fbs_order_detail(posting_number)
            return detail

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取FBS订单详情失败: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取FBS订单详情错误: {str(e)}",
        )


@router.get("/orders/unfulfilled", response_model=List[Dict[str, Any]])
async def get_unfulfilled_postings(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    获取待发货订单列表

    获取所有未完成的订单（待发货）。
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

    # 获取店铺
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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(status_code=400, detail="店铺缺少Ozon API凭证")

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        async with adapter:
            postings = await adapter.get_unfulfilled_postings()
            return postings

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待发货订单失败: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取待发货订单错误: {str(e)}",
        )


class OzonWarehouseResponse(BaseModel):
    """Ozon仓库响应"""

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
    """Ozon配送方式响应"""

    delivery_method_id: str
    name: str
    warehouse_id: str
    warehouse_name: Optional[str] = None
    price: float = 0

    class Config:
        from_attributes = True


class OzonSellerInfoResponse(BaseModel):
    """Ozon卖家信息响应"""

    seller_id: int
    name: str
    company: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True


@router.get("/warehouses", response_model=List[OzonWarehouseResponse])
async def get_ozon_warehouses(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonWarehouseResponse]:
    """
    获取Ozon仓库列表
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"获取仓库失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库错误: {str(e)}",
        )


@router.get("/delivery-methods", response_model=List[OzonDeliveryMethodResponse])
async def get_ozon_delivery_methods(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OzonDeliveryMethodResponse]:
    """
    获取Ozon配送方式列表
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"获取配送方式失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配送方式错误: {str(e)}",
        )


@router.get("/seller-info", response_model=OzonSellerInfoResponse)
async def get_ozon_seller_info(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OzonSellerInfoResponse:
    """
    获取Ozon卖家信息
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"获取卖家信息失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取卖家信息错误: {str(e)}",
        )


class OzonPriceUpdateRequest(BaseModel):
    """Ozon价格更新请求"""

    offer_id: str
    price: float
    old_price: Optional[float] = None
    marketing_price: Optional[float] = None


class OzonStockUpdateRequest(BaseModel):
    """Ozon库存更新请求"""

    offer_id: str
    stock: int
    warehouse_id: Optional[str] = None


@router.post("/products/prices", response_model=Dict[str, Any])
async def update_ozon_product_prices(
    items: List[OzonPriceUpdateRequest],
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    批量更新Ozon商品价格
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
                "message": f"成功提交{len(items)}个商品价格更新",
            }

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新价格失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新价格错误: {str(e)}",
        )


@router.post("/products/stocks", response_model=Dict[str, Any])
async def update_ozon_product_stocks(
    items: List[OzonStockUpdateRequest],
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    批量更新Ozon商品库存
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
                "message": f"成功提交{len(items)}个商品库存更新",
            }

    except OzonIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新库存失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新库存错误: {str(e)}",
        )


@router.get("/products/prices", response_model=List[Dict[str, Any]])
async def get_ozon_product_prices(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    product_ids: Optional[str] = Query(
        default=None, description="商品ID列表，逗号分隔"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    获取Ozon商品价格信息
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"获取价格失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取价格错误: {str(e)}",
        )


@router.get("/products/stocks", response_model=List[Dict[str, Any]])
async def get_ozon_product_stocks(
    shop_id: Optional[str] = Query(default=None, description="店铺ID"),
    product_ids: Optional[str] = Query(
        default=None, description="商品ID列表，逗号分隔"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    获取Ozon商品库存信息
    """
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="用户未在任何团队中")

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
            raise HTTPException(status_code=404, detail="Ozon店铺不存在")
    else:
        result = await db.execute(
            select(Shop).where(
                and_(Shop.team_id == member.team_id, Shop.platform == "ozon")
            )
        )
        shop = result.scalars().first()
        if not shop:
            raise HTTPException(
                status_code=404, detail="未找到Ozon店铺，请先添加Ozon店铺"
            )

    try:
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            raise HTTPException(
                status_code=400, detail="店铺缺少Ozon API凭证，请检查店铺配置"
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
            detail=f"获取库存失败: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取库存错误: {str(e)}",
        )
