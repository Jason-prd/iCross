#!/usr/bin/env python3
"""测试店铺验证端点"""

import asyncio
import os
import sys
from sqlalchemy import select

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_shop_validation():
    from app.core.database import async_session_maker
    from app.models.database import Shop
    
    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shop = result.scalars().first()
        
        if not shop:
            print("ERROR: No Ozon shop found")
            return
        
        print(f"Shop: {shop.name} (ID: {shop.id})")
        print(f"Current platform_shop_id: {shop.platform_shop_id}")
        print(f"Current platform_shop_name: {shop.platform_shop_name}")
        
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")
        print(f"Client ID: {client_id}")
        
        # 导入验证函数（模拟端点逻辑）
        from app.integrations.ozon.adapter import OzonIntegrationAdapter
        from app.integrations.ozon.exceptions import OzonIntegrationError
        
        if not client_id or not api_key:
            print("ERROR: Missing API credentials")
            return
        
        try:
            adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
            async with adapter:
                # 测试连接
                connected = await adapter.connect()
                print(f"Connection successful: {connected}")
                
                # 尝试获取一个订单
                from datetime import datetime, timedelta
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=1)
                try:
                    fbo_orders = await adapter.get_fbo_orders(start_date, end_date, limit=1)
                    print(f"FBO orders found: {len(fbo_orders)}")
                    if fbo_orders:
                        print(f"First order posting_number: {fbo_orders[0].get('order_id')}")
                except Exception as e:
                    print(f"FBO order fetch error: {e}")
                
                # 尝试获取FBS订单
                try:
                    fbs_orders = await adapter.get_fbs_orders(start_date, end_date, limit=1)
                    print(f"FBS orders found: {len(fbs_orders)}")
                except Exception as e:
                    print(f"FBS order fetch error: {e}")
                    
        except Exception as e:
            print(f"Adapter error: {e}")
            import traceback
            traceback.print_exc()
        
        # 模拟更新platform_shop_id
        if not shop.platform_shop_id and client_id:
            shop.platform_shop_id = str(client_id)
            print(f"Would update platform_shop_id to: {shop.platform_shop_id}")
            # 实际需要db.commit()
        
        if not shop.platform_shop_name:
            shop.platform_shop_name = shop.name
            print(f"Would update platform_shop_name to: {shop.platform_shop_name}")

async def main():
    print("Testing shop validation logic...")
    await test_shop_validation()

if __name__ == "__main__":
    asyncio.run(main())