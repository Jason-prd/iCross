import asyncio
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


async def test_adapter_fixed():
    """测试修复后的适配器"""
    try:
        from app.integrations.ozon.adapter import OzonIntegrationAdapter

        client_id = "2867211"
        api_key = "6d13a910-3e64-4954-bd70-3b46e9f38841"

        print(f"Testing OzonIntegrationAdapter with client_id: {client_id}")

        try:
            adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
            print("[OK] Adapter created successfully")

            # 测试连接
            print("\nTesting connect()...")
            try:
                connected = await adapter.connect()
                print(f"[OK] connect() returned: {connected}")
                print(f"Adapter connected: {adapter._connected}")
                print(f"Adapter API: {adapter._api}")

                # 测试断开连接
                await adapter.disconnect()
                print("[OK] disconnect() successful")

                return True
            except Exception as e:
                print(f"[ERROR] connect() failed: {type(e).__name__}: {str(e)}")
                import traceback

                traceback.print_exc()
                return False

        except Exception as e:
            print(f"[ERROR] Failed to create adapter: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_adapter_fixed())
    sys.exit(0 if success else 1)
