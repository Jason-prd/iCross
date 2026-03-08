#!/usr/bin/env python3
"""测试Ozon适配器连接"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_adapter():
    """测试适配器连接"""
    from app.integrations.ozon.adapter import OzonIntegrationAdapter

    # 使用配置中的凭证（来自.env）
    adapter = OzonIntegrationAdapter()

    try:
        async with adapter:
            connected = await adapter.connect()
            if connected:
                print("SUCCESS: Adapter connected successfully")

                # 测试获取产品
                print("Fetching products...")
                products = await adapter.get_all_products()
                print(f"SUCCESS: Got {len(products)} products")

                # 显示前几个产品
                for i, product in enumerate(products[:5]):
                    print(
                        f"  Product {i+1}: ID={product.get('product_id')}, Name={product.get('name')[:30]}"
                    )

                if len(products) > 5:
                    print(f"  ... and {len(products) - 5} more")
            else:
                print("ERROR: Adapter failed to connect")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


async def main():
    """主函数"""
    print("Testing Ozon adapter connection...")
    await test_adapter()


if __name__ == "__main__":
    asyncio.run(main())
