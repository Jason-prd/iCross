import asyncio

import aiohttp


async def test_network_connection():
    """测试网络连接和Ozon API端点"""
    url = "https://api-seller.ozon.ru"

    print(f"Testing network connection to: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            # 首先测试基本连接
            print("\n1. Testing basic connection (HEAD request)...")
            try:
                async with session.head(url, timeout=10) as response:
                    print(f"   Status: {response.status}")
                    print(f"   Headers: {dict(response.headers)}")
            except Exception as e:
                print(f"   [ERROR] HEAD request failed: {type(e).__name__}: {e}")

            # 测试API端点
            print("\n2. Testing API endpoint (without auth)...")
            try:
                api_url = f"{url}/v1/description-category/tree"
                headers = {
                    "Client-Id": "test",
                    "Api-Key": "test",
                    "Content-Type": "application/json",
                }
                async with session.post(
                    api_url, headers=headers, json={}, timeout=10
                ) as response:
                    print(f"   Status: {response.status}")
                    print(f"   Response headers: {dict(response.headers)}")
                    try:
                        text = await response.text()
                        print(f"   Response (first 200 chars): {text[:200]}")
                    except Exception:
                        print("   Could not read response text")
            except Exception as e:
                print(f"   [ERROR] API request failed: {type(e).__name__}: {e}")
                import traceback

                traceback.print_exc()

    except Exception as e:
        print(f"[ERROR] Session error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_network_connection())
