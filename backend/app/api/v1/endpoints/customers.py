import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.database import Customer, CustomerCommunication, TeamMember, User

router = APIRouter()


class CustomerResponse(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    customer_type: str = "retail"
    level: str = "normal"
    tags: List[str] = []
    total_orders: int = 0
    total_spent: float = 0
    last_order_date: Optional[str] = None
    created_at: str


class CommunicationCreate(BaseModel):
    type: str
    direction: str
    subject: Optional[str] = None
    content: str
    follow_up_action: Optional[str] = None
    follow_up_date: Optional[str] = None


class CommunicationResponse(BaseModel):
    id: str
    type: str
    direction: str
    subject: Optional[str] = None
    content: str
    status: str
    follow_up_action: Optional[str] = None
    follow_up_date: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str


class PaginatedResponse(BaseModel):
    data: List[CustomerResponse]
    meta: Dict[str, Any]


@router.get("", response_model=PaginatedResponse)
async def get_customers(
    segment: Optional[str] = None,
    level: Optional[str] = None,
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

    query = select(Customer).where(Customer.team_id == member.team_id)

    if level:
        query = query.where(Customer.level == level)
    if q:
        query = query.where(
            (Customer.name.ilike(f"%{q}%"))
            | (Customer.email.ilike(f"%{q}%"))
            | (Customer.phone.ilike(f"%{q}%"))
        )

    count_query = select(Customer).where(Customer.team_id == member.team_id)
    total_result = await db.execute(count_query)
    total = len(total_result.all())

    query = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .order_by(Customer.created_at.desc())
    )
    result = await db.execute(query)
    customers = result.scalars().all()

    return PaginatedResponse(
        data=[
            CustomerResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                company=c.company,
                customer_type=c.customer_type,
                level=c.level,
                tags=c.tags,
                total_orders=c.total_orders,
                total_spent=float(c.total_spent),
                last_order_date=(
                    c.last_order_date.isoformat() if c.last_order_date else None
                ),
                created_at=c.created_at.isoformat(),
            )
            for c in customers
        ],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
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
        select(Customer).where(
            and_(Customer.id == customer_id, Customer.team_id == member.team_id)
        )
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        company=customer.company,
        customer_type=customer.customer_type,
        level=customer.level,
        tags=customer.tags,
        total_orders=customer.total_orders,
        total_spent=float(customer.total_spent),
        last_order_date=(
            customer.last_order_date.isoformat() if customer.last_order_date else None
        ),
        created_at=customer.created_at.isoformat(),
    )


@router.post("/{customer_id}/communications", response_model=CommunicationResponse)
async def add_communication(
    customer_id: str,
    comm_data: CommunicationCreate,
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
        select(Customer).where(
            and_(Customer.id == customer_id, Customer.team_id == member.team_id)
        )
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    communication = CustomerCommunication(
        id=str(uuid.uuid4()),
        team_id=member.team_id,
        customer_id=customer_id,
        type=comm_data.type,
        direction=comm_data.direction,
        subject=comm_data.subject,
        content=comm_data.content,
        sender_id=current_user.id,
        status="completed",
        follow_up_action=comm_data.follow_up_action,
        follow_up_date=(
            datetime.fromisoformat(comm_data.follow_up_date)
            if comm_data.follow_up_date
            else None
        ),
    )
    db.add(communication)
    await db.commit()
    await db.refresh(communication)

    return CommunicationResponse(
        id=communication.id,
        type=communication.type,
        direction=communication.direction,
        subject=communication.subject,
        content=communication.content,
        status=communication.status,
        follow_up_action=communication.follow_up_action,
        follow_up_date=(
            communication.follow_up_date.isoformat()
            if communication.follow_up_date
            else None
        ),
        created_by=current_user.id,
        created_at=communication.created_at.isoformat(),
    )


@router.get("/{customer_id}/communications")
async def get_customer_communications(
    customer_id: str,
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
        select(Customer).where(
            and_(Customer.id == customer_id, Customer.team_id == member.team_id)
        )
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    result = await db.execute(
        select(CustomerCommunication)
        .where(CustomerCommunication.customer_id == customer_id)
        .order_by(CustomerCommunication.created_at.desc())
    )
    communications = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "type": c.type,
                "direction": c.direction,
                "subject": c.subject,
                "content": c.content,
                "status": c.status,
                "follow_up_action": c.follow_up_action,
                "follow_up_date": (
                    c.follow_up_date.isoformat() if c.follow_up_date else None
                ),
                "created_at": c.created_at.isoformat(),
            }
            for c in communications
        ],
    }
