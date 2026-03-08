import asyncio
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.database import Shop, TeamMember, User


async def test_sync_endpoint_logic():
    """测试同步端点中使用的逻辑"""
    async with async_session_maker() as session:
        # 首先找到一个用户和团队
        result = await session.execute(select(User))
        user = result.scalars().first()

        if not user:
            print("No users found in database")
            return

        print(f"Found user: {user.id}, email: {user.email}")

        # 找到团队成员关系
        result = await session.execute(
            select(TeamMember).where(
                TeamMember.user_id == user.id, TeamMember.status == "active"
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            print("User is not a member of any team")
            return

        print(f"Found team member: team_id={member.team_id}")

        # 现在模拟ozon.py中的查询
        result = await session.execute(
            select(Shop).where(Shop.team_id == member.team_id, Shop.platform == "ozon")
        )
        shop = result.scalars().first()

        print("\nShop query result:")
        print(f"  Shop found: {shop is not None}")
        if shop:
            print(f"  Shop ID: {shop.id}")
            print(f"  Shop name: {shop.name}")
            print(f"  API credentials type: {type(shop.api_credentials)}")
            print(f"  API credentials: {shop.api_credentials}")

            # 测试实际代码中的逻辑
            try:
                client_id = shop.api_credentials.get("client_id")
                api_key = shop.api_credentials.get("api_key")
                print(f"  client_id: {client_id}")
                print(
                    f"  api_key (first 10 chars): {api_key[:10] if api_key else 'None'}"
                )

                if not client_id or not api_key:
                    print("  ERROR: Missing client_id or api_key!")
                else:
                    print("  SUCCESS: API credentials extracted successfully")
            except Exception as e:
                print(f"  ERROR extracting credentials: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_sync_endpoint_logic())
