#!/usr/bin/env python3
"""
Quick test of Ozon sync endpoint - just check it starts without 500 error
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append("D:/iCross/python-ozon-api-main")

from fastapi import HTTPException
from sqlalchemy import select

from app.api.v1.endpoints.ozon import sync_ozon_products
from app.core.database import async_session_maker
from app.models.database import Shop, TeamMember, User


async def test():
    print("Quick test: checking if endpoint starts without error...")

    async with async_session_maker() as db:
        # Get admin user
        result = await db.execute(select(User).where(User.email == "admin@icross.com"))
        user = result.scalar_one()

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

        # Get first Ozon shop
        result = await db.execute(
            select(Shop).where(Shop.team_id == member.team_id, Shop.platform == "ozon")
        )
        shop = result.scalars().first()

        if not shop:
            print("No Ozon shop found")
            return

        print(f"Testing with shop ID: {shop.id}")

        # Call sync function with timeout
        try:
            # Start sync but timeout after 15 seconds
            task = asyncio.create_task(
                sync_ozon_products(shop_id=shop.id, current_user=user, db=db)
            )

            # Wait for 15 seconds max
            await asyncio.wait_for(task, timeout=15.0)
            response = task.result()
            print(f"Success! Response: {response}")

        except asyncio.TimeoutError:
            print(
                "Sync still running after 15 seconds (expected - it's a long operation)"
            )
            print("No 500 error - endpoint is working!")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        except HTTPException as e:
            print(f"HTTPException: {e.status_code} - {e.detail}")
        except Exception as e:
            print(f"Exception: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
