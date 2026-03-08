#!/usr/bin/env python3
"""调试Ozon同步错误"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def debug_sync_error():
    """调试同步错误"""
    from sqlalchemy import select

    from app.core.database import async_session_maker
    from app.models.database import Shop

    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shops = result.scalars().all()

        print(f"找到 {len(shops)} 个Ozon店铺")

        for shop in shops:
            print(f"\n店铺ID: {shop.id}")
            print(f"店铺名称: {shop.name}")
            print(f"API凭证类型: {type(shop.api_credentials)}")
            print(f"API凭证: {shop.api_credentials}")

            client_id = (
                shop.api_credentials.get("client_id") if shop.api_credentials else None
            )
            api_key = (
                shop.api_credentials.get("api_key") if shop.api_credentials else None
            )

            print(f"Client ID: {client_id}")
            print(f"API Key: {api_key}")

            # 测试适配器
            if client_id and api_key:
                from app.integrations.ozon.adapter import OzonIntegrationAdapter

                try:
                    adapter = OzonIntegrationAdapter(
                        client_id=client_id, api_key=api_key
                    )
                    async with adapter:
                        connected = await adapter.connect()
                        if connected:
                            print("✅ 适配器连接成功")

                            # 尝试获取产品
                            try:
                                products = await adapter.get_all_products()
                                print(f"✅ 获取到 {len(products)} 个产品")
                            except Exception as e:
                                print(f"❌ 获取产品失败: {str(e)}")
                                import traceback

                                traceback.print_exc()
                        else:
                            print("❌ 适配器连接失败")
                except Exception as e:
                    print(f"❌ 适配器错误: {str(e)}")
                    import traceback

                    traceback.print_exc()
            else:
                print("❌ 凭证缺失或不全")


async def main():
    """主函数"""
    print("调试Ozon同步错误...")
    await debug_sync_error()


if __name__ == "__main__":
    asyncio.run(main())
