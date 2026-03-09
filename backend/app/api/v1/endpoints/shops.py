import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import Shop, ShopSyncLog, TeamMember, User

router = APIRouter()


class ShopCreate(BaseModel):
    platform: str
    name: str
    api_credentials: Dict[str, Any]


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    sync_settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ShopResponse(BaseModel):
    id: str
    name: str
    platform: str
    platform_shop_id: Optional[str] = None
    platform_shop_name: Optional[str] = None
    status: str
    last_sync_time: Optional[str] = None
    last_sync_status: Optional[str] = None
    api_quota_used: int = 0
    api_quota_limit: Optional[int] = None
    created_at: str


class SyncResponse(BaseModel):
    task_id: str
    status: str
    message: str


class ShopValidationResponse(BaseModel):
    """Shop validation response"""

    success: bool
    message: str
    platform_shop_id: Optional[str] = None
    platform_shop_name: Optional[str] = None
    connection_tested: bool = False
    order_read_permission: Optional[bool] = None
    orders_found: Optional[int] = None


@router.get("", response_model=List[ShopResponse])
async def get_shops(
    platform: Optional[str] = None,
    status: Optional[str] = None,
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

    query = select(Shop).where(Shop.team_id == member.team_id)

    if platform:
        query = query.where(Shop.platform == platform)
    if status:
        query = query.where(Shop.status == status)

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    shops = result.scalars().all()

    return [
        ShopResponse(
            id=s.id,
            name=s.name,
            platform=s.platform,
            platform_shop_id=s.platform_shop_id,
            platform_shop_name=s.platform_shop_name,
            status=s.status,
            last_sync_time=s.last_sync_time.isoformat() if s.last_sync_time else None,
            last_sync_status=s.last_sync_status,
            api_quota_used=s.api_quota_used,
            api_quota_limit=s.api_quota_limit,
            created_at=s.created_at.isoformat(),
        )
        for s in shops
    ]


@router.post("", response_model=ShopResponse)
async def create_shop(
    shop_data: ShopCreate,
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
        raise HTTPException(status_code=403, detail="No permission to create shop")

    # Set platform shop ID and name
    platform_shop_id = None
    platform_shop_name = shop_data.name

    if shop_data.platform == "ozon" and shop_data.api_credentials:
        # For Ozon platform, use client_id as platform shop ID
        platform_shop_id = shop_data.api_credentials.get("client_id")
        # If no shop name, can use client_id or leave as None
        if platform_shop_id and not platform_shop_name:
            platform_shop_name = f"Ozon Shop {platform_shop_id}"

    shop = Shop(
        id=str(uuid.uuid4()),
        team_id=member.team_id,
        name=shop_data.name,
        platform=shop_data.platform,
        platform_shop_id=platform_shop_id,
        platform_shop_name=platform_shop_name,
        api_credentials=shop_data.api_credentials,
        status="active",
    )
    db.add(shop)
    await db.commit()
    await db.refresh(shop)

    return ShopResponse(
        id=shop.id,
        name=shop.name,
        platform=shop.platform,
        platform_shop_id=shop.platform_shop_id,
        platform_shop_name=shop.platform_shop_name,
        status=shop.status,
        last_sync_time=shop.last_sync_time.isoformat() if shop.last_sync_time else None,
        last_sync_status=shop.last_sync_status,
        api_quota_used=shop.api_quota_used,
        api_quota_limit=shop.api_quota_limit,
        created_at=shop.created_at.isoformat(),
    )


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: str,
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
        select(Shop).where(and_(Shop.id == shop_id, Shop.team_id == member.team_id))
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    return ShopResponse(
        id=shop.id,
        name=shop.name,
        platform=shop.platform,
        platform_shop_id=shop.platform_shop_id,
        platform_shop_name=shop.platform_shop_name,
        status=shop.status,
        last_sync_time=shop.last_sync_time.isoformat() if shop.last_sync_time else None,
        last_sync_status=shop.last_sync_status,
        api_quota_used=shop.api_quota_used,
        api_quota_limit=shop.api_quota_limit,
        created_at=shop.created_at.isoformat(),
    )


@router.patch("/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: str,
    shop_data: ShopUpdate,
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
        select(Shop).where(and_(Shop.id == shop_id, Shop.team_id == member.team_id))
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    if shop_data.name is not None:
        shop.name = shop_data.name
    if shop_data.settings is not None:
        shop.settings = shop_data.settings
    if shop_data.sync_settings is not None:
        shop.sync_settings = shop_data.sync_settings
    if shop_data.status is not None:
        shop.status = shop_data.status

    await db.commit()
    await db.refresh(shop)

    return ShopResponse(
        id=shop.id,
        name=shop.name,
        platform=shop.platform,
        platform_shop_id=shop.platform_shop_id,
        platform_shop_name=shop.platform_shop_name,
        status=shop.status,
        last_sync_time=shop.last_sync_time.isoformat() if shop.last_sync_time else None,
        last_sync_status=shop.last_sync_status,
        api_quota_used=shop.api_quota_used,
        api_quota_limit=shop.api_quota_limit,
        created_at=shop.created_at.isoformat(),
    )


@router.delete("/{shop_id}")
async def delete_shop(
    shop_id: str,
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
        raise HTTPException(status_code=403, detail="No permission to delete shop")

    result = await db.execute(
        select(Shop).where(and_(Shop.id == shop_id, Shop.team_id == member.team_id))
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    await db.delete(shop)
    await db.commit()

    return {"success": True, "message": "Shop deleted successfully"}


@router.post("/{shop_id}/sync", response_model=SyncResponse)
async def sync_shop(
    shop_id: str,
    sync_type: str = Query("full", regex="^(full|incremental)$"),
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
        select(Shop).where(and_(Shop.id == shop_id, Shop.team_id == member.team_id))
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    task_id = str(uuid.uuid4())

    sync_log = ShopSyncLog(
        id=str(uuid.uuid4()),
        shop_id=shop_id,
        sync_type="product",
        sync_mode="manual",
        status="queued",
    )
    db.add(sync_log)
    await db.commit()

    return SyncResponse(
        task_id=task_id, status="queued", message="Sync task has been queued"
    )


@router.post("/{shop_id}/validate", response_model=ShopValidationResponse)
async def validate_shop(
    shop_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShopValidationResponse:
    """Validate shop connection and permissions"""
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = await db.execute(
        select(Shop).where(and_(Shop.id == shop_id, Shop.team_id == member.team_id))
    )
    shop = result.scalar_one_or_none()

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Validate based on platform
    if shop.platform == "ozon":
        from app.integrations.ozon.adapter import OzonIntegrationAdapter
        from app.integrations.ozon.exceptions import OzonIntegrationError

        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            return ShopValidationResponse(
                success=False,
                message="Missing Ozon API credentials (client_id or api_key)",
                platform_shop_id=shop.platform_shop_id,
                platform_shop_name=shop.platform_shop_name,
                connection_tested=False,
            )

        try:
            adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
            async with adapter:
                # Test connection
                connected = await adapter.connect()
                if not connected:
                    return ShopValidationResponse(
                        success=False,
                        message="Failed to connect to Ozon API",
                        platform_shop_id=shop.platform_shop_id,
                        platform_shop_name=shop.platform_shop_name,
                        connection_tested=True,
                    )

                # Try to get an order to verify order read permission
                orders_found = 0
                order_read_permission = False
                try:
                    # Try to get FBO orders from last 1 day (max 1)
                    from datetime import datetime, timedelta

                    end_date = datetime.utcnow()
                    start_date = end_date - timedelta(days=1)
                    fbo_orders = await adapter.get_fbo_orders(
                        start_date, end_date, limit=1
                    )
                    if isinstance(fbo_orders, list):
                        orders_found = len(fbo_orders)
                        order_read_permission = True
                except Exception as order_error:
                    # Failed to get orders, may be due to insufficient permissions or no orders
                    order_read_permission = False

                # Update shop platform ID and name (if missing)
                updated = False
                if not shop.platform_shop_id and client_id:
                    shop.platform_shop_id = str(client_id)
                    updated = True
                if not shop.platform_shop_name:
                    shop.platform_shop_name = shop.name
                    updated = True

                if updated:
                    await db.commit()

                return ShopValidationResponse(
                    success=True,
                    message="Shop validated successfully",
                    platform_shop_id=shop.platform_shop_id,
                    platform_shop_name=shop.platform_shop_name,
                    connection_tested=True,
                    order_read_permission=order_read_permission,
                    orders_found=orders_found,
                )

        except OzonIntegrationError as e:
            return ShopValidationResponse(
                success=False,
                message=f"Ozon integration error: {e.message}",
                platform_shop_id=shop.platform_shop_id,
                platform_shop_name=shop.platform_shop_name,
                connection_tested=True,
            )
        except Exception as e:
            return ShopValidationResponse(
                success=False,
                message=f"Unexpected error: {str(e)}",
                platform_shop_id=shop.platform_shop_id,
                platform_shop_name=shop.platform_shop_name,
                connection_tested=False,
            )
    else:
        # Other platforms not supported for validation yet
        return ShopValidationResponse(
            success=False,
            message=f"Platform {shop.platform} validation not implemented yet",
            platform_shop_id=shop.platform_shop_id,
            platform_shop_name=shop.platform_shop_name,
            connection_tested=False,
        )
