#!/usr/bin/env python3
"""
Test Ozon sync endpoint directly
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append("D:/iCross/python-ozon-api-main")

from fastapi import HTTPException
from sqlalchemy import select

from app.api.v1.endpoints.ozon import sync_ozon_products
from app.core.database import async_session_maker, init_db
from app.models.database import Shop, TeamMember, User


async def test():
    print("Testing Ozon sync endpoint directly...")

    await init_db()

    # Get admin user
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.email == "admin@icross.com"))
        user = result.scalar_one()

        print(f"User: {user.email}")

        # Get user's team member record
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == user.id, TeamMember.status == "active"
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            print("User not in any team")
            return

        print(f"Team ID: {member.team_id}")

        # Get Ozon shop
        result = await db.execute(
            select(Shop).where(Shop.team_id == member.team_id, Shop.platform == "ozon")
        )
        shops = result.scalars().all()

        if not shops:
            print("No Ozon shop found")
            return

        # Use first shop
        shop = shops[0]
        print(f"Shop ID: {shop.id}")

        # Now call the sync function directly
        try:
            response = await sync_ozon_products(
                shop_id=shop.id, current_user=user, db=db
            )
            print(f"Success! Response: {response}")
        except HTTPException as e:
            print(f"HTTPException: {e.status_code} - {e.detail}")
        except Exception as e:
            print(f"Exception: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
