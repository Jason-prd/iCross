#!/usr/bin/env python3
"""
Test Ozon sync endpoint
"""

import asyncio
import os
import sys

import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_ozon_sync():
    # First, login to get token
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Login
        login_data = {"username": "admin@icross.com", "password": "admin123"}

        print("Logging in...")
        try:
            login_response = await client.post("/api/v1/auth/login", data=login_data)
            login_response.raise_for_status()
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"Got access token: {access_token[:20]}...")
        except Exception as e:
            print(f"Login failed: {e}")
            if hasattr(e, "response"):
                print(f"Response: {e.response.text}")
            return

        # Test Ozon sync products endpoint
        headers = {"Authorization": f"Bearer {access_token}"}

        print("\nTesting Ozon sync products endpoint...")
        try:
            # First try without shop_id to see if we have any Ozon shops
            sync_response = await client.post(
                "/api/v1/ozon/sync/products",
                headers=headers,
                params={},  # No shop_id, should use default
            )
            sync_response.raise_for_status()
            print(f"Sync successful: {sync_response.json()}")
        except Exception as e:
            print(f"Sync failed: {e}")
            if hasattr(e, "response"):
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")

            # Try to get Ozon shops first
            print("\nTrying to get Ozon shops...")
            try:
                shops_response = await client.get("/api/v1/shops", headers=headers)
                shops_response.raise_for_status()
                shops = shops_response.json()
                print(f"Found shops: {shops}")

                # Filter for Ozon shops
                ozon_shops = [s for s in shops if s.get("platform") == "ozon"]
                print(f"Ozon shops: {ozon_shops}")

                if ozon_shops:
                    shop_id = ozon_shops[0]["id"]
                    print(f"\nTrying sync with shop_id: {shop_id}")
                    sync_response = await client.post(
                        "/api/v1/ozon/sync/products",
                        headers=headers,
                        params={"shop_id": shop_id},
                    )
                    sync_response.raise_for_status()
                    print(f"Sync successful: {sync_response.json()}")
            except Exception as e2:
                print(f"Shops fetch failed: {e2}")
                if hasattr(e2, "response"):
                    print(f"Response: {e2.response.text}")


if __name__ == "__main__":
    asyncio.run(test_ozon_sync())
