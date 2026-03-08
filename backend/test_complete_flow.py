# -*- coding: utf-8 -*-
"""
完整流程测试 - 展示三大功能
1. Ozon API上架
2. 定时任务
3. 1688代发逻辑
"""
import sys
sys.path.insert(0, r'D:\iCross\backend')
import os
os.environ['DATABASE_TYPE'] = 'sqlite'

from datetime import datetime


def test_ozon_listing():
    """测试Ozon API上架"""
    print("=" * 60)
    print("[1] Ozon API Listing Service")
    print("=" * 60)
    
    from app.services.ozon_listing import create_ozon_listing_service
    
    service = create_ozon_listing_service()
    
    # 检查配置
    shop = service.get_shop()
    print(f"\n[Config]")
    print(f"  Shop: {shop.name if shop else 'Not found'}")
    print(f"  Platform: {shop.platform if shop else 'N/A'}")
    print(f"  Client ID: {shop.api_credentials.get('client_id') if shop else 'N/A'}")
    
    # 获取适配器
    adapter = service.get_ozon_adapter()
    print(f"  Ozon Adapter: {'OK' if adapter else 'Failed'}")
    
    service.close()
    print("\n")


def test_scheduler():
    """测试定时任务"""
    print("=" * 60)
    print("[2] Task Scheduler")
    print("=" * 60)
    
    from app.services.scheduler import get_task_schedule, run_scheduled_task
    
    # 显示任务列表
    print("\n[Registered Tasks]")
    schedule = get_task_schedule()
    for name, status in schedule.items():
        print(f"  - {name}")
        print(f"    Interval: {status['interval_minutes']} minutes")
    
    # 测试运行
    print("\n[Test Run: sync_orders]")
    result = run_scheduled_task("sync_orders")
    print(f"  Result: {result.get('message', result.get('error', 'OK'))}")
    
    print("\n")


def test_ali1688_dropship():
    """测试1688代发"""
    print("=" * 60)
    print("[3] 1688 Dropship Service")
    print("=" * 60)
    
    from app.services.ali1688_dropship import ali1688_service, order_processor
    import asyncio
    
    # 测试URL解析
    print("\n[Test URL Parsing]")
    test_urls = [
        "https://detail.1688.com/offer/123456789.html",
        "https://detail.1688.com/offer/640034987890.html?spm=...",
    ]
    
    for url in test_urls:
        result = ali1688_service.parse_1688_url(url)
        print(f"  {url[:50]}...")
        print(f"    Valid: {result.get('valid')}")
        if result.get('valid'):
            print(f"    Offer ID: {result.get('offer_id')}")
    
    # 测试订单创建（模拟）
    print("\n[Test Order Creation (Simulated)]")
    
    async def test_order():
        result = await order_processor.process_new_order(
            ozon_order_id="123456789",
            sku="SKU#0828104003-1",
            quantity=1,
            sale_price=500.0,
            buyer_info={
                "name": "Test Buyer",
                "phone": "+7900000000",
                "address": "Moscow, Russia"
            }
        )
        return result
    
    result = asyncio.run(test_order())
    print(f"  Result: {result}")
    
    print("\n")


def test_integration():
    """测试完整流程"""
    print("=" * 60)
    print("[4] Full Integration Test")
    print("=" * 60)
    
    # 模拟完整流程
    print("\n[Simulated Flow]")
    print("  1. Order received from Ozon")
    print("  2. Match SKU to 1688 supplier link")
    print("  3. Calculate profit")
    print("  4. Create 1688 order")
    print("  5. Get tracking number")
    print("  6. Update Ozon with tracking")
    print("  7. Update local order status")
    
    print("\n  [Mock Result]")
    print("    Ozon Order: 123456789")
    print("    SKU: SKU#0828104003-1")
    print("    Sale Price: 500 RUB")
    print("    Cost: 200 RUB")
    print("    Profit: 300 RUB (60%)")
    print("    Status: Shipped")
    
    print("\n")


def main():
    print("\n" + "=" * 60)
    print(" iCross Complete Flow Test")
    print("=" * 60 + "\n")
    
    # 1. Ozon API上架
    test_ozon_listing()
    
    # 2. 定时任务
    test_scheduler()
    
    # 3. 1688代发
    test_ali1688_dropship()
    
    # 4. 完整集成
    test_integration()
    
    print("=" * 60)
    print(" ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Configure 1688 API credentials")
    print("  2. Set up Celery for production")
    print("  3. Test real Ozon listing")
    print("  4. Test real 1688 orders\n")


if __name__ == "__main__":
    main()
