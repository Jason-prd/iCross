import asyncio
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


async def test_ozon_connection():
    """测试Ozon API连接并捕获详细错误"""
    try:
        from ozon_api import OzonAPI
        from ozon_api.exceptions import OzonAPIError

        client_id = "2867211"
        api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"

        print(f"Testing Ozon API connection with client_id: {client_id}")
        print(f"API key (first 10 chars): {api_key[:10]}...")

        # 尝试创建API实例
        print("\n1. Creating OzonAPI instance...")
        try:
            api = OzonAPI(client_id=client_id, api_key=api_key)
            print("   [OK] OzonAPI instance created")
            print(f"   API object: {api}")
            print(f"   API type: {type(api)}")
        except Exception as e:
            print(f"   [ERROR] Error creating OzonAPI: {type(e).__name__}: {e}")
            print(f"   Exception dir: {dir(e)}")
            if hasattr(e, "__dict__"):
                print(f"   Exception dict: {e.__dict__}")
            return

        # 尝试连接
        print("\n2. Testing connection with get_description_category_tree()...")
        try:
            # 使用异步上下文管理器
            async with api:
                print("   [OK] Entered async context")
                # 添加超时
                try:
                    result = await asyncio.wait_for(
                        api.get_description_category_tree(), timeout=30.0
                    )
                    print("   [OK] get_description_category_tree() succeeded")
                    print(f"   Result type: {type(result)}")
                    if hasattr(result, "result"):
                        print("   Has result attribute: True")
                        print(f"   Result: {result.result}")
                    else:
                        print(f"   Result: {result}")
                except asyncio.TimeoutError:
                    print(
                        "   [ERROR] get_description_category_tree() timed out after 30 seconds"
                    )
                    return
                except OzonAPIError as e:
                    print(f"   [ERROR] OzonAPIError: {type(e).__name__}")
                    print(f"   Error message: {e.message}")
                    print(f"   Error type: {e}")
                    print(f"   Exception dir: {dir(e)}")
                    return
                except Exception as e:
                    print(
                        f"   [ERROR] General Exception in get_description_category_tree(): {type(e).__name__}: {e}"
                    )
                    print(f"   str(e): '{str(e)}'")
                    print(f"   repr(e): '{repr(e)}'")
                    print(f"   Exception dir: {dir(e)}")
                    if hasattr(e, "__dict__"):
                        print(f"   Exception dict: {e.__dict__}")
                    import traceback

                    traceback.print_exc()
                    return
        except Exception as e:
            print(f"   [ERROR] Exception in async context: {type(e).__name__}: {e}")
            print(f"   str(e): '{str(e)}'")
            import traceback

            traceback.print_exc()

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print(
            "Make sure ozon-api is installed: pip install -e D:/iCross/python-ozon-api-main"
        )
    except Exception as e:
        print(f"[ERROR] General error: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ozon_connection())
