import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import func, select

from app.core.database import async_session_maker
from app.models.database import OzonProduct


async def check():
    async with async_session_maker() as db:
        result = await db.execute(select(func.count()).select_from(OzonProduct))
        count = result.scalar()
        print(f"Total Ozon products: {count}")


asyncio.run(check())
