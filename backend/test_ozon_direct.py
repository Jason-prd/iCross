import asyncio
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加python-ozon-api-main到路径
sys.path.insert(0, os.path.join(current_dir, "python-ozon-api-main"))
sys.path.insert(0, current_dir)


async def test_direct_api():
    """直接测试Ozon API库"""
    try:
        from ozon_api import OzonAPI

        client_id = "2867211"
        api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"

        print(f"Creating OzonAPI with client_id: {client_id}")

        # 使用异步上下文管理器
        async with OzonAPI(client_id=client_id, api_key=api_key) as api:
            print("OzonAPI created successfully")

            # 测试分类树（带超时）
            try:
                print("Testing get_description_category_tree() with timeout...")
                tree = await asyncio.wait_for(
                    api.get_description_category_tree(), timeout=10.0
                )
                print("Category tree received successfully")
                print(f"Has result attribute: {hasattr(tree, 'result')}")
                if hasattr(tree, "result"):
                    print(f"Result type: {type(tree.result)}")
                    if isinstance(tree.result, list):
                        print(f"Number of categories: {len(tree.result)}")
            except asyncio.TimeoutError:
                print(
                    "ERROR: get_description_category_tree() timed out after 10 seconds"
                )
            except Exception as e:
                print(
                    f"ERROR in get_description_category_tree(): {type(e).__name__}: {str(e)}"
                )
                import traceback

                traceback.print_exc()

            # 测试产品列表（带超时）
            try:
                print("\nTesting product_list() with timeout...")
                from ozon_api.models.product_list import (
                    ProductListFilter,
                    ProductListRequest,
                )

                filters = ProductListFilter(visibility="ALL")
                request = ProductListRequest(
                    filter=filters, limit=5, last_id=""  # 只获取5个产品
                )

                response = await asyncio.wait_for(
                    api.product_list(request), timeout=10.0
                )
                print("Product list response received")
                print(f"Has result: {hasattr(response, 'result')}")
                if hasattr(response, "result") and hasattr(response.result, "items"):
                    print(f"Number of items: {len(response.result.items)}")
                    for i, item in enumerate(response.result.items[:3]):
                        print(
                            f"  Item {i+1}: product_id={item.get('product_id')}, offer_id={item.get('offer_id')}"
                        )
            except asyncio.TimeoutError:
                print("ERROR: product_list() timed out after 10 seconds")
            except Exception as e:
                print(f"ERROR in product_list(): {type(e).__name__}: {str(e)}")
                import traceback

                traceback.print_exc()

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure python-ozon-api-main is in the Python path")
    except Exception as e:
        print(f"General error: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_api())
