#!/usr/bin/env python3
"""综合测试FBO订单API"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fbo_comprehensive():
    """综合测试FBO API"""
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

        print(f"Shop: {shop.name} (ID: {shop.id})")
        print(f"Platform Shop ID: {shop.platform_shop_id}")
        print(f"Platform Shop Name: {shop.platform_shop_name}")
        
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")
        
        print(f"Client ID: {client_id}")
        
        # 直接使用ozon_api库测试
        try:
            sys.path.append("D:/iCross/python-ozon-api-main")
            from ozon_api import OzonAPI
            
            # 创建API客户端
            api = OzonAPI(client_id=client_id, api_key=api_key)
            
            print("\n=== 开始FBO订单API测试 ===")
            
            # 测试不同时间范围
            time_ranges = [
                ("最近1天", 1),
                ("最近7天", 7),
                ("最近30天", 30),
                ("最近90天", 90),
                ("最近180天", 180),
                ("所有时间", None),  # 不传时间参数
            ]
            
            # Ozon订单可能的状态
            status_list = [
                None,  # 所有状态
                "awaiting_packaging",
                "awaiting_deliver", 
                "delivering",
                "delivered",
                "cancelled",
                "arbitration",
            ]
            
            async with api:
                for range_name, days in time_ranges:
                    print(f"\n--- 时间范围: {range_name} ---")
                    
                    # 构建请求参数
                    filter_data = {}
                    if days:
                        end_date = datetime.utcnow()
                        start_date = end_date - timedelta(days=days)
                        filter_data["since"] = start_date.isoformat() + "Z"
                        filter_data["to"] = end_date.isoformat() + "Z"
                    
                    for status in status_list:
                        current_filter = filter_data.copy()
                        if status:
                            current_filter["status"] = status
                        
                        payload = {
                            "filter": current_filter,
                            "limit": 50
                        }
                        
                        print(f"  状态 '{status or 'all'}': ", end="", flush=True)
                        
                        try:
                            response = await api._request(
                                method="post",
                                api_version="v2",
                                endpoint="posting/fbo/list",
                                json=payload,
                                timeout=10
                            )
                            
                            if isinstance(response, dict) and "result" in response:
                                orders = response["result"]
                                if isinstance(orders, list):
                                    print(f"找到 {len(orders)} 个订单")
                                    if orders and len(orders) > 0:
                                        print(f"    第一个订单ID: {orders[0].get('posting_number', 'N/A')}")
                                        print(f"    状态: {orders[0].get('status', 'N/A')}")
                                        print(f"    创建时间: {orders[0].get('created_at', 'N/A')}")
                                else:
                                    print(f"result不是列表: {type(orders)}")
                            else:
                                print(f"响应格式异常: {response}")
                                
                        except Exception as e:
                            print(f"API错误: {str(e)[:100]}")
                
                # 测试其他可能的端点
                print(f"\n=== 测试其他可能的相关端点 ===")
                
                # 端点列表
                endpoints = [
                    "posting/fbo/list",
                    "v2/posting/fbo/list",
                    "v2/fbo/list",
                    "v2/order/list",
                    "v2/posting/order/list",
                ]
                
                # 使用简单参数
                test_payload = {"limit": 10}
                
                for endpoint in endpoints:
                    print(f"  端点 '{endpoint}': ", end="", flush=True)
                    try:
                        # 尝试不同格式的端点
                        if endpoint.startswith("v2/"):
                            api_ver = "v2"
                            endp = endpoint[3:]  # 去掉v2/
                        else:
                            api_ver = "v2"
                            endp = endpoint
                        
                        response = await api._request(
                            method="post",
                            api_version=api_ver,
                            endpoint=endp,
                            json=test_payload,
                            timeout=8
                        )
                        
                        if isinstance(response, dict):
                            if "result" in response:
                                orders = response["result"]
                                if isinstance(orders, list):
                                    print(f"找到 {len(orders)} 个订单")
                                    if orders:
                                        print(f"    成功! 端点有效")
                                        break
                                else:
                                    print(f"result不是列表")
                            else:
                                print(f"无result字段，响应键: {list(response.keys())}")
                        else:
                            print(f"响应类型: {type(response)}")
                            
                    except Exception as e:
                        print(f"错误: {str(e)[:80]}")
                
                # 测试获取订单统计信息
                print(f"\n=== 测试订单统计 ===")
                try:
                    # 尝试获取订单统计
                    stats_response = await api._request(
                        method="post",
                        api_version="v2",
                        endpoint="v2/posting/fbo/unfulfilled/list",
                        json={"limit": 10},
                        timeout=8
                    )
                    print(f"未完成订单统计: {stats_response}")
                except Exception as e:
                    print(f"未完成订单统计错误: {str(e)[:80]}")
                    
        except ImportError as e:
            print(f"无法导入ozon_api: {e}")
        except Exception as e:
            print(f"其他错误: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    print("综合测试FBO订单API...")
    await test_fbo_comprehensive()

if __name__ == "__main__":
    asyncio.run(main())