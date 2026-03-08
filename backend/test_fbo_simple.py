#!/usr/bin/env python3
"""简单测试FBO订单API"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fbo_simple():
    """简单测试FBO API"""
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
        
        client_id = shop.api_credentials.get("client_id")
        api_key = shop.api_credentials.get("api_key")
        
        print(f"Client ID: {client_id}")
        
        # 直接使用ozon_api库测试
        try:
            sys.path.append("D:/iCross/python-ozon-api-main")
            from ozon_api import OzonAPI
            
            # 创建API客户端
            api = OzonAPI(client_id=client_id, api_key=api_key)
            
            # 测试连接
            print("\nTesting Ozon API connection...")
            
            # 构建请求参数 - 测试最近30天
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            filter_data = {
                "since": start_date.isoformat() + "Z",
                "to": end_date.isoformat() + "Z"
            }
            
            payload = {
                "filter": filter_data,
                "limit": 100
            }
            
            print(f"API请求参数: {payload}")
            
            # 直接调用API
            async with api:
                print("Making API request to /v2/posting/fbo/list...")
                try:
                    response = await api._request(
                        method="post",
                        api_version="v2",
                        endpoint="posting/fbo/list",
                        json=payload
                    )
                    
                    print(f"\nAPI响应类型: {type(response)}")
                    print(f"API响应内容: {response}")
                    
                    if isinstance(response, dict):
                        print(f"\n响应键: {list(response.keys())}")
                        if "result" in response:
                            result_data = response["result"]
                            print(f"result字段类型: {type(result_data)}")
                            if isinstance(result_data, list):
                                print(f"订单数量: {len(result_data)}")
                                if result_data:
                                    print("第一个订单示例:")
                                    import json
                                    print(json.dumps(result_data[0], indent=2, ensure_ascii=False))
                            else:
                                print(f"result不是列表: {result_data}")
                        else:
                            print("响应中没有result字段")
                    else:
                        print(f"响应不是字典: {response}")
                        
                except Exception as e:
                    print(f"API请求失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
        except ImportError as e:
            print(f"无法导入ozon_api: {e}")
            print("请检查python-ozon-api-main路径")
        except Exception as e:
            print(f"其他错误: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    print("简单测试FBO订单API...")
    await test_fbo_simple()

if __name__ == "__main__":
    asyncio.run(main())