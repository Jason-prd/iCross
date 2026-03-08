#!/usr/bin/env python3
"""诊断FBO订单API问题"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def diagnose_fbo_orders():
    """诊断FBO订单API"""
    from sqlalchemy import select
    from app.core.database import async_session_maker
    from app.models.database import Shop
    from app.integrations.ozon.adapter import OzonIntegrationAdapter

    async with async_session_maker() as db:
        # 查找Ozon店铺
        result = await db.execute(select(Shop).where(Shop.platform == "ozon"))
        shop = result.scalars().first()

        if not shop:
            print("ERROR: No Ozon shop found")
            return

        print(f"Shop ID: {shop.id}")
        print(f"Shop name: {shop.name}")
        print(f"Shop platform: {shop.platform}")

        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")

        if not client_id or not api_key:
            print("ERROR: Shop missing API credentials")
            return

        print(f"Client ID: {client_id}")
        print(f"API Key: {api_key[:10]}...")

        # 测试适配器
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

        try:
            async with adapter:
                connected = await adapter.connect()
                if not connected:
                    print("ERROR: Failed to connect to Ozon API")
                    return

                print("\nSUCCESS: Connected to Ozon API")

                # 测试不同时间范围的FBO订单
                time_ranges = [
                    ("最近1天", 1),
                    ("最近7天", 7),
                    ("最近30天", 30),
                    ("最近90天", 90),
                ]
                
                for range_name, days in time_ranges:
                    end_date = datetime.utcnow()
                    start_date = end_date - timedelta(days=days)
                    
                    print(f"\n=== 测试 {range_name} ({days}天) ===")
                    print(f"时间范围: {start_date} 到 {end_date}")
                    
                    try:
                        # 直接调用API方法
                        fbo_orders = await adapter.get_fbo_orders(
                            start_date=start_date, 
                            end_date=end_date, 
                            limit=50
                        )
                        print(f"获取到 {len(fbo_orders)} 个FBO订单")
                        
                        if fbo_orders:
                            print("前5个订单示例:")
                            for i, order in enumerate(fbo_orders[:5]):
                                print(f"  订单{i+1}: ID={order.get('order_id')}, "
                                      f"编号={order.get('order_number')}, "
                                      f"状态={order.get('status')}, "
                                      f"金额={order.get('total_amount')}")
                        else:
                            print("未获取到订单，检查API响应...")
                            # 可以尝试直接调用API查看原始响应
                            
                    except Exception as e:
                        print(f"获取{range_name}订单时出错: {str(e)}")
                        import traceback
                        traceback.print_exc()

                # 测试无时间限制的FBO订单
                print(f"\n=== 测试无时间限制 (仅限最近100个订单) ===")
                try:
                    fbo_orders = await adapter.get_fbo_orders(limit=100)
                    print(f"获取到 {len(fbo_orders)} 个FBO订单")
                    
                    if fbo_orders:
                        print("订单统计:")
                        status_counts = {}
                        for order in fbo_orders:
                            status = order.get('status', 'unknown')
                            status_counts[status] = status_counts.get(status, 0) + 1
                        
                        for status, count in status_counts.items():
                            print(f"  状态 '{status}': {count} 个订单")
                    else:
                        print("警告: 即使无时间限制也未获取到订单")
                        
                except Exception as e:
                    print(f"获取无时间限制订单时出错: {str(e)}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    print("开始诊断FBO订单API问题...")
    await diagnose_fbo_orders()

if __name__ == "__main__":
    asyncio.run(main())