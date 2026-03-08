#!/usr/bin/env python3
"""测试Ozon订单同步"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_order_sync():
    """测试订单同步"""
    from sqlalchemy import select

    from app.core.database import async_session_maker
    from app.models.database import Shop

    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shop = result.scalars().first()

        if not shop:
            print("ERROR: No Ozon shop found")
            return

        print(f"Shop ID: {shop.id}")
        print(f"Shop name: {shop.name}")

        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            print("ERROR: Shop missing API credentials")
            return

        print(f"Client ID: {client_id[:10]}...")

        # 测试适配器订单方法
        from app.integrations.ozon.adapter import OzonIntegrationAdapter

        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        try:
            async with adapter:
                connected = await adapter.connect()
                if not connected:
                    print("ERROR: Failed to connect to Ozon API")
                    return

                print("SUCCESS: Connected to Ozon API")

                # 测试获取FBO订单
                print("\nTesting FBO orders...")
                try:
                    fbo_orders = await adapter.get_fbo_orders(limit=10)
                    print(f"Got {len(fbo_orders)} FBO orders")
                    if fbo_orders:
                        print(f"First order ID: {fbo_orders[0].get('order_id', 'N/A')}")
                except Exception as e:
                    print(f"ERROR getting FBO orders: {str(e)}")

                # 测试获取FBS订单
                print("\nTesting FBS orders...")
                try:
                    fbs_orders = await adapter.get_fbs_orders(limit=10)
                    print(f"Got {len(fbs_orders)} FBS orders")
                    if fbs_orders:
                        print(f"First order ID: {fbs_orders[0].get('order_id', 'N/A')}")
                except Exception as e:
                    print(f"ERROR getting FBS orders: {str(e)}")

                # 测试同步订单到数据库
                print("\nTesting order sync to database...")
                try:
                    sync_result = await adapter.sync_orders_to_database(
                        db=db, team_id=shop.team_id, shop_id=shop.id, days_back=1
                    )
                    print(f"Sync result: {sync_result}")
                except Exception as e:
                    print(f"ERROR syncing orders: {str(e)}")
                    import traceback

                    traceback.print_exc()

        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback

            traceback.print_exc()


async def main():
    """主函数"""
    print("Testing Ozon order synchronization...")
    await test_order_sync()


if __name__ == "__main__":
    asyncio.run(main())
