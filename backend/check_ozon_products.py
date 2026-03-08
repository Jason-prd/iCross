#!/usr/bin/env python3
"""
Check Ozon products in database
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session_maker
from app.models.database import OzonProduct


async def check():
    async with async_session_maker() as db:
        from sqlalchemy import func, select

        result = await db.execute(select(func.count()).select_from(OzonProduct))
        count = result.scalar()
        print(f"Total Ozon products in database: {count}")

        # Show some sample products
        if count > 0:
            result = await db.execute(select(OzonProduct).limit(5))
            products = result.scalars().all()
            for p in products:
                print(f"  - {p.offer_id}: {p.name}")


if __name__ == "__main__":
    asyncio.run(check())
