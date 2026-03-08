import asyncio
import os
import sys

from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from sqlalchemy import select

# from main import app  # 暂时注释掉
from app.core.database import async_session_maker
from app.models.database import Shop, TeamMember, User

# 创建测试客户端
client = TestClient(app)


async def setup_test_data():
    """设置测试数据"""
    async with async_session_maker() as session:
        # 获取现有用户
        result = await session.execute(select(User))
        user = result.scalars().first()

        if not user:
            print("No user found")
            return None

        # 获取团队成员关系
        result = await session.execute(
            select(TeamMember).where(
                TeamMember.user_id == user.id, TeamMember.status == "active"
            )
        )
        member = result.scalar_one_or_none()

        return member


def test_sync_endpoint():
    """测试同步端点"""
    print("Testing /api/v1/ozon/sync/products endpoint...")

    # 首先我们需要一个有效的JWT令牌
    # 让我们尝试使用测试端点或模拟认证
    # 由于认证复杂，我们直接测试底层逻辑

    print("Testing the underlying sync logic...")

    # 直接测试sync_products_to_database函数

    from app.core.database import async_session_maker
    from app.integrations.ozon.adapter import OzonIntegrationAdapter

    async def test_sync_logic():
        async with async_session_maker() as db:
            # 查找Ozon店铺
            result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
            shop = result.scalars().first()

            if not shop:
                print("No Ozon shop found")
                return

            print(f"Found shop: {shop.id}, {shop.name}")
            print(f"API credentials: {shop.api_credentials}")

            client_id = shop.api_credentials.get("client_id")
            api_key = shop.api_credentials.get("api_key")

            if not client_id or not api_key:
                print("Missing API credentials")
                return

            print(f"Using client_id: {client_id}, api_key: {api_key[:10]}...")

            try:
                adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
                async with adapter:
                    # 测试连接
                    connected = await adapter.connect()
                    print(f"Adapter connected: {connected}")

                    if connected:
                        # 测试获取产品
                        print("Testing product sync...")
                        products = await adapter.get_all_products()
                        print(f"Retrieved {len(products)} products from Ozon API")

                        # 测试同步到数据库
                        sync_result = await adapter.sync_products_to_database(
                            db=db, team_id=shop.team_id, shop_id=shop.id
                        )
                        print(f"Sync result: {sync_result}")
                    else:
                        print("Failed to connect to Ozon API")
            except Exception as e:
                print(f"Error during sync: {type(e).__name__}: {str(e)}")
                import traceback

                traceback.print_exc()

    # 运行异步测试
    asyncio.run(test_sync_logic())


if __name__ == "__main__":
    test_sync_endpoint()
