import asyncio
import json
from datetime import datetime, timedelta

import aiohttp


async def test_ozon_orders():
    """直接测试Ozon订单API"""
    client_id = "2867211"
    api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"

    # 计算时间范围（最近7天）
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    # 测试FBO订单
    url_fbo = "https://api-seller.ozon.ru/v2/posting/fbo/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }

    # FBO请求体
    payload_fbo = {
        "filter": {
            "since": start_date.isoformat() + "Z",
            "to": end_date.isoformat() + "Z",
        },
        "limit": 10,
    }

    print("Testing FBO orders API")
    print(f"URL: {url_fbo}")
    print(f"Headers: Client-Id={client_id}, Api-Key={api_key[:10]}...")
    print(f"Payload: {json.dumps(payload_fbo, indent=2)}")

    try:
        async with aiohttp.ClientSession() as session:
            print("\nSending POST request to FBO API...")
            async with session.post(
                url_fbo, headers=headers, json=payload_fbo, timeout=30
            ) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")

                body_bytes = await response.read()
                text = body_bytes.decode("utf-8")
                print(f"Response length: {len(text)} chars")

                if response.status == 200:
                    try:
                        data = json.loads(text)
                        print("\nParsed JSON response:")
                        print(f"Response keys: {list(data.keys())}")
                        if "result" in data:
                            result = data["result"]
                            if isinstance(result, list):
                                print(f"Number of orders: {len(result)}")
                                if result:
                                    print(
                                        f"First order (truncated): {json.dumps(result[0], ensure_ascii=False)[:500]}"
                                    )
                            else:
                                print(f"Result type: {type(result)}")
                                print(
                                    f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}"
                                )
                        else:
                            print("No 'result' key found")
                            print(
                                f"Full response (truncated): {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}"
                            )
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Raw text (first 1000 chars): {text[:1000]}")
                else:
                    print(f"Error response: {text}")

    except Exception as e:
        print(f"[ERROR] Request failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

    # 测试FBS订单
    url_fbs = "https://api-seller.ozon.ru/v2/posting/fbs/list"
    payload_fbs = {
        "filter": {
            "since": start_date.isoformat() + "Z",
            "to": end_date.isoformat() + "Z",
        },
        "limit": 10,
    }

    print("\n\nTesting FBS orders API")
    print(f"URL: {url_fbs}")
    print(f"Payload: {json.dumps(payload_fbs, indent=2)}")

    try:
        async with aiohttp.ClientSession() as session:
            print("\nSending POST request to FBS API...")
            async with session.post(
                url_fbs, headers=headers, json=payload_fbs, timeout=30
            ) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")

                body_bytes = await response.read()
                text = body_bytes.decode("utf-8")
                print(f"Response length: {len(text)} chars")

                if response.status == 200:
                    try:
                        data = json.loads(text)
                        print("\nParsed JSON response:")
                        print(f"Response keys: {list(data.keys())}")
                        if "result" in data:
                            result = data["result"]
                            if isinstance(result, list):
                                print(f"Number of orders: {len(result)}")
                                if result:
                                    print(
                                        f"First order (truncated): {json.dumps(result[0], ensure_ascii=False)[:500]}"
                                    )
                            else:
                                print(f"Result type: {type(result)}")
                                print(
                                    f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}"
                                )
                        else:
                            print("No 'result' key found")
                            print(
                                f"Full response (truncated): {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}"
                            )
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Raw text (first 1000 chars): {text[:1000]}")
                else:
                    print(f"Error response: {text}")

    except Exception as e:
        print(f"[ERROR] Request failed: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ozon_orders())
