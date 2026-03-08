import asyncio
import json

import aiohttp


async def test_ozon_api_direct():
    """直接测试Ozon API"""
    client_id = "2867211"
    api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"
    url = "https://api-seller.ozon.ru/v1/description-category/tree"

    print("Testing Ozon API directly")
    print(f"Client-ID: {client_id}")
    print(f"API-Key: {api_key[:10]}...")
    print(f"URL: {url}")

    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            print("\nSending POST request to Ozon API...")
            async with session.post(
                url, headers=headers, json={}, timeout=30
            ) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")

                try:
                    # 使用read()而不是text()，设置更长的超时
                    print("Reading response body...")
                    body_bytes = await response.read()
                    print(f"Response body read: {len(body_bytes)} bytes")

                    try:
                        text = body_bytes.decode("utf-8")
                        print(f"Response text length: {len(text)} chars")
                        print(f"First 500 chars: {text[:500]}")

                        if response.status == 200:
                            try:
                                data = json.loads(text)
                                print("\nParsed JSON response:")
                                print(f"Response keys: {list(data.keys())}")
                                if "result" in data:
                                    result = data["result"]
                                    if isinstance(result, list):
                                        print(f"Number of categories: {len(result)}")
                                        if result:
                                            print(
                                                f"First category: {json.dumps(result[0], ensure_ascii=False)[:200]}"
                                            )
                                    else:
                                        print(f"Result type: {type(result)}")
                                        print(f"Result: {result}")
                                else:
                                    print(
                                        f"Full response (truncated): {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}"
                                    )
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                                print(f"Raw text (first 1000 chars): {text[:1000]}")
                        else:
                            print(f"Error response: {text}")
                    except UnicodeDecodeError:
                        print("Could not decode response as UTF-8")
                        print(f"Hex dump (first 100 bytes): {body_bytes[:100].hex()}")
                except asyncio.TimeoutError:
                    print("[ERROR] Timeout reading response body")
                except Exception as e:
                    print(f"Error reading response: {type(e).__name__}: {e}")
                    import traceback

                    traceback.print_exc()

    except asyncio.TimeoutError:
        print("[ERROR] Request timed out after 30 seconds")
    except Exception as e:
        print(f"[ERROR] Request failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ozon_api_direct())
