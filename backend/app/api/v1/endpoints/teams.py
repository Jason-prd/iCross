import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import Team, TeamMember, User

router = APIRouter()


class TeamMemberResponse(BaseModel):
    id: str
    email: str
    name: str = None
    role: str
    status: str
    joined_at: str = None


class TeamResponse(BaseModel):
    id: str
    name: str
    description: str = None
    logo_url: str = None
    subscription_plan: str = "basic"
    max_members: int = 5


class TeamUpdate(BaseModel):
    name: str = None
    description: str = None
    logo_url: str = None


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "operator"


class UpdateMemberRoleRequest(BaseModel):
    role: str


@router.get("", response_model=TeamResponse)
async def get_current_team(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=404, detail="User not in any team")

    result = await db.execute(select(Team).where(Team.id == member.team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        logo_url=team.logo_url,
        subscription_plan=team.subscription_plan,
        max_members=team.max_members,
    )


@router.put("", response_model=TeamResponse)
async def update_team(
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id,
            TeamMember.status == "active",
            TeamMember.role == "super_admin",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only super admin can update team")

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    member = result.scalar_one()

    result = await db.execute(select(Team).where(Team.id == member.team_id))
    team = result.scalar_one()

    if team_data.name:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    if team_data.logo_url is not None:
        team.logo_url = team_data.logo_url

    await db.commit()
    await db.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        logo_url=team.logo_url,
        subscription_plan=team.subscription_plan,
        max_members=team.max_members,
    )


@router.get("/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
        select(TeamMember, User)
        .join(User, TeamMember.user_id == User.id)
        .where(TeamMember.team_id == member.team_id)
    )
    members = result.all()

    return [
        TeamMemberResponse(
            id=m[0].id,
            email=m[1].email,
            name=m[1].name,
            role=m[0].role,
            status=m[0].status,
            joined_at=m[0].joined_at.isoformat() if m[0].joined_at else None,
        )
        for m in members
    ]


@router.post("/members", response_model=TeamMemberResponse)
async def invite_member(
    invite_data: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id,
            TeamMember.status == "active",
            TeamMember.role.in_(["super_admin", "admin"]),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Only admins can invite members")

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id, TeamMember.status == "active"
        )
    )
    current_member = result.scalar_one()

    result = await db.execute(select(Team).where(Team.id == current_member.team_id))
    team = result.scalar_one()

    result = await db.execute(select(TeamMember).where(TeamMember.team_id == team.id))
    member_count = len(result.all())

    if member_count >= team.max_members:
        raise HTTPException(status_code=400, detail="Team member limit reached")

    result = await db.execute(select(User).where(User.email == invite_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == current_member.team_id,
                TeamMember.user_id == existing_user.id,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already in team")

        new_member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=current_member.team_id,
            user_id=existing_user.id,
            role=invite_data.role,
            status="active",
            invited_by=current_user.id,
            joined_at=None,
        )
    else:
        new_user = User(
            id=str(uuid.uuid4()),
            email=invite_data.email,
            password_hash="",
            name=invite_data.email.split("@")[0],
        )
        db.add(new_user)
        await db.flush()

        new_member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=current_member.team_id,
            user_id=new_user.id,
            role=invite_data.role,
            status="invited",
            invited_by=current_user.id,
            invited_at=None,
        )

    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    return TeamMemberResponse(
        id=new_member.id,
        email=invite_data.email,
        name=invite_data.email.split("@")[0],
        role=new_member.role,
        status=new_member.status,
    )


@router.patch("/members/{member_id}/role", response_model=TeamMemberResponse)
async def update_member_role(
    member_id: str,
    role_data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == current_user.id,
            TeamMember.status == "active",
            TeamMember.role == "super_admin",
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=403, detail="Only super admin can update member roles"
        )

    result = await db.execute(select(TeamMember).where(TeamMember.id == member_id))
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot change super admin role")

    member.role = role_data.role
    await db.commit()
    await db.refresh(member)

    result = await db.execute(select(User).where(User.id == member.user_id))
    user = result.scalar_one()

    return TeamMemberResponse(
        id=member.id,
        email=user.email,
        name=user.name,
        role=member.role,
        status=member.status,
        joined_at=member.joined_at.isoformat() if member.joined_at else None,
    )
