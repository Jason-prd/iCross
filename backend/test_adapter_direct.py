#!/usr/bin/env python3
"""
Test Ozon adapter directly
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append("D:/iCross/python-ozon-api-main")

from app.core.database import async_session_maker, init_db
from app.integrations.ozon.adapter import OzonIntegrationAdapter


async def test_adapter():
    print("Testing Ozon adapter directly...")

    # Initialize database
    await init_db()

    # Create a database session
    async with async_session_maker() as db:
        # We need a team_id and shop_id
        # Let's check what teams and shops exist
        from sqlalchemy import select

        from app.models.database import Shop, Team

        result = await db.execute(select(Team))
        teams = result.scalars().all()

        if not teams:
            print("No teams found in database")
            return

        team_id = teams[0].id
        print(f"Using team_id: {team_id}")

        # Check for Ozon shops
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shops = result.scalars().all()

        if not shops:
            print("No Ozon shops found in database")
            print("Creating a test Ozon shop...")
            # Create a test shop
            from uuid import uuid4

            shop = Shop(
                id=str(uuid4()),
                team_id=team_id,
                name="Test Ozon Shop",
                platform="ozon",
                platform_shop_id="b65c85d1-6915-4c9c-b273-fd94e7973a4a",  # Test shop ID
                credentials={
                    "client_id": 2867211,
                    "api_key": "6d13a910-3e64-4954-bd70-3b46e9f38841",
                },
                status="active",
                settings={},
            )
            db.add(shop)
            await db.commit()
            shop_id = shop.id
            print(f"Created test shop with ID: {shop_id}")
        else:
            shop_id = shops[0].id
            print(f"Using existing Ozon shop ID: {shop_id}")

        # Test the adapter
        try:
            adapter = OzonIntegrationAdapter()

            async with adapter:
                print("Syncing products to database...")
                result = await adapter.sync_products_to_database(
                    db=db, team_id=team_id, shop_id=shop_id
                )
                print(f"Sync result: {result}")

        except Exception as e:
            print(f"Error during sync: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_adapter())
