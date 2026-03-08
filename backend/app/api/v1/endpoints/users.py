from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import User

router = APIRouter()


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = "Asia/Shanghai"
    language: Optional[str] = "zh-CN"
    currency: Optional[str] = "CNY"


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"
    currency: str = "CNY"
    status: str = "active"


@router.get("", response_model=UserResponse)
async def get_users(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        language=current_user.language,
        currency=current_user.currency,
        status=current_user.status,
    )


@router.put("", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url
    if user_data.timezone is not None:
        current_user.timezone = user_data.timezone
    if user_data.language is not None:
        current_user.language = user_data.language
    if user_data.currency is not None:
        current_user.currency = user_data.currency

    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        language=current_user.language,
        currency=current_user.currency,
        status=current_user.status,
    )
