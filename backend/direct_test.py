import asyncio
import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from sqlalchemy import select

from app.core.database import async_session_maker
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.models.database import Shop


async def test_sync():
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
                    print("Connected successfully!")
                    # 只测试获取少量产品（第一页）
                    try:
                        print("Testing product listing (first page only)...")
                        # 调用原始API方法获取第一页

                        from ozon_api.models.product_list import (
                            ProductListFilters,
                            ProductListRequest,
                        )

                        filters = ProductListFilters(visibility="ALL")

                        request = ProductListRequest(
                            filter=filters,
                            limit=10,  # 只获取10个产品测试
                            last_id="",
                            sort_dir="ASC",
                        )

                        response = await adapter.api.product.get_list(request)
                        print(
                            f"API response received: {len(response.result.items) if response and response.result else 0} products"
                        )

                        # 测试同步到数据库（但只同步少量数据）
                        print("Testing sync to database (limited)...")
                        sync_result = await adapter.sync_products_to_database(
                            db=db, team_id=shop.team_id, shop_id=shop.id, limit=10
                        )
                        print(f"Sync result: {sync_result}")
                    except Exception as e2:
                        print(
                            f"Error in product sync test: {type(e2).__name__}: {str(e2)}"
                        )
                        import traceback

                        traceback.print_exc()
                else:
                    print("Failed to connect to Ozon API")
        except Exception as e:
            print(f"Error during sync: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sync())
