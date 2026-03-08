#!/usr/bin/env python3
"""检查店铺详情"""

import asyncio
import os
import sys
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def check_shop():
    """检查店铺详情"""
    from sqlalchemy import select
    from app.core.database import async_session_maker
    from app.models.database import Shop

    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shops = result.scalars().all()

        if not shops:
            print("ERROR: No Ozon shop found")
            return

        for shop in shops:
            print(f"\n=== 店铺详情 ===")
            print(f"ID: {shop.id}")
            print(f"名称: {shop.name}")
            print(f"平台: {shop.platform}")
            print(f"平台店铺ID: {shop.platform_shop_id}")
            print(f"平台店铺名称: {shop.platform_shop_name}")
            print(f"状态: {shop.status}")
            print(f"最后同步时间: {shop.last_sync_time}")
            print(f"最后同步状态: {shop.last_sync_status}")
            print(f"API配额使用: {shop.api_quota_used}/{shop.api_quota_limit}")
            
            # API凭证
            creds = shop.api_credentials
            print(f"\nAPI凭证:")
            if isinstance(creds, dict):
                for key, value in creds.items():
                    if key in ['api_key', 'secret']:
                        print(f"  {key}: {value[:10]}... (隐藏)")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  {creds}")
            
            # 设置
            print(f"\n设置:")
            print(f"  {shop.settings}")
            
            # 同步设置
            print(f"\n同步设置:")
            print(f"  {shop.sync_settings}")
            
            # 额外数据
            print(f"\n店铺额外数据:")
            print(f"  {shop.shop_extra_data}")

async def main():
    """主函数"""
    print("检查店铺详情...")
    await check_shop()

if __name__ == "__main__":
    asyncio.run(main())