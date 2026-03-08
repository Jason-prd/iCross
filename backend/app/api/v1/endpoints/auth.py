import traceback
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.database import Team, TeamMember, User, UserSession

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = None
    team_name: str = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: str = None
    avatar_url: str = None
    role: str = None
    team_id: str = None
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"
    currency: str = "CNY"


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def get_current_team(current_user: User = Depends(get_current_user)) -> Team:
    result = (
        await get_db()
        .__aenter__()
        .execute(select(TeamMember).where(TeamMember.user_id == current_user.id))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="User not in any team")

    result = (
        await get_db()
        .__aenter__()
        .execute(select(Team).where(Team.id == member.team_id))
    )
    return result.scalar_one()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            name=user_data.name,
        )
        db.add(user)
        await db.flush()

        team_name = user_data.team_name or f"{user_data.name}'s Team"
        team = Team(
            id=str(uuid.uuid4()),
            name=team_name,
        )
        db.add(team)
        await db.flush()

        member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=team.id,
            user_id=user.id,
            role="super_admin",
            status="active",
            joined_at=datetime.utcnow(),
        )
        db.add(member)
        await db.commit()

        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": "super_admin",
                "team_id": team.id,
            },
        )
    except Exception as e:
        print(f"Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    print(f"DEBUG login attempt: username={form_data.username}")
    try:
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        user.last_login_at = datetime.utcnow()
        await db.commit()

        result = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == user.id, TeamMember.status == "active"
            )
        )
        member = result.scalar_one_or_none()

        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})

        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow()
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": member.role if member else None,
                "team_id": member.team_id if member else None,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": member.role if member else None,
            "team_id": member.team_id if member else None,
        },
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    result = (
        await get_db()
        .__aenter__()
        .execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id, TeamMember.status == "active"
            )
        )
    )
    member = result.scalar_one_or_none()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        role=member.role if member else None,
        team_id=member.team_id if member else None,
    )
