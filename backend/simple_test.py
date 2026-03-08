import asyncio
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


async def test_connection():
    """简单测试连接"""
    from app.integrations.ozon.adapter import OzonIntegrationAdapter

    # 使用.env文件中的凭证
    client_id = "2867211"
    api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"

    print(f"Testing connection with client_id: {client_id}")
    print(f"API key (first 10 chars): {api_key[:10]}...")

    try:
        adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
        async with adapter:
            print("Adapter created")

            # 测试连接
            connected = await adapter.connect()
            print(f"Connected: {connected}")

            if connected:
                print("Testing category tree...")
                # 直接调用API方法
                try:
                    from ozon_api import OzonAPI

                    api = OzonAPI(client_id=client_id, api_key=api_key)

                    # 测试分类树
                    print("Getting category tree...")
                    tree = await api.get_description_category_tree()
                    print(
                        f"Category tree received: {len(tree.result) if hasattr(tree, 'result') else 'unknown'}"
                    )

                    # 测试简单的产品列表（只获取少量）
                    print("\nTesting product list (limit 5)...")
                    from ozon_api.models.product_list import (
                        ProductListFilter,
                        ProductListRequest,
                    )

                    filters = ProductListFilter(visibility="ALL")
                    request = ProductListRequest(
                        filter=filters, limit=5, last_id=""  # 只获取5个产品
                    )

                    response = await api.product_list(request)
                    print("Product list response received")
                    print(f"Has result: {hasattr(response, 'result')}")
                    if hasattr(response, "result") and hasattr(
                        response.result, "items"
                    ):
                        print(f"Number of items: {len(response.result.items)}")
                        for i, item in enumerate(response.result.items[:3]):
                            print(
                                f"  Item {i+1}: product_id={item.get('product_id')}, offer_id={item.get('offer_id')}"
                            )

                except Exception as e2:
                    print(f"Error in API calls: {type(e2).__name__}: {str(e2)}")
                    import traceback

                    traceback.print_exc()

    except Exception as e:
        print(f"Error creating adapter: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())
