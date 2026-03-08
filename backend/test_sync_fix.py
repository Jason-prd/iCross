#!/usr/bin/env python3
"""测试Ozon同步端点修复"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.models.database import Shop


async def test_shop_credentials():
    """测试店铺凭证"""
    from sqlalchemy import select

    from app.core.database import async_session_maker

    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shops = result.scalars().all()

        print(f"找到 {len(shops)} 个Ozon店铺")

        for shop in shops:
            print(f"\n店铺ID: {shop.id}")
            print(f"店铺名称: {shop.name}")
            print(f"平台店铺ID: {shop.platform_shop_id}")
            print(f"API凭证: {shop.api_credentials}")

            # 检查凭证
            client_id = shop.api_credentials.get("client_id")
            api_key = shop.api_credentials.get("api_key")

            if client_id and api_key:
                print(
                    f"✅ 凭证存在: client_id={client_id[:10]}..., api_key={api_key[:10]}..."
                )

                # 测试适配器连接
                try:
                    adapter = OzonIntegrationAdapter(
                        client_id=client_id, api_key=api_key
                    )
                    async with adapter:
                        connected = await adapter.connect()
                        if connected:
                            print("✅ 适配器连接成功")

                            # 测试获取产品数量
                            products = await adapter.get_all_products()
                            print(f"✅ 获取到 {len(products)} 个产品")
                        else:
                            print("❌ 适配器连接失败")
                except Exception as e:
                    print(f"❌ 适配器错误: {str(e)}")
            else:
                print("❌ 凭证缺失或不全")


async def main():
    """主函数"""
    print("测试Ozon同步修复...")
    await test_shop_credentials()


if __name__ == "__main__":
    asyncio.run(main())
