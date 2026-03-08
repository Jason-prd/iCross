#!/usr/bin/env python3
"""
测试登录功能的脚本
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import verify_password
from app.models.database import User


async def test_login():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        email = "admin@icross.com"
        password = "admin123"

        print(f"Testing login for {email}")

        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print("User not found!")
            return

        print(f"User found: {user.email}")
        print(f"Password hash: {user.password_hash[:50]}...")

        try:
            is_valid = verify_password(password, user.password_hash)
            print(f"Password valid: {is_valid}")
        except Exception as e:
            print(f"Password verification error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_login())
