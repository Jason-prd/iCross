import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


async def test_sync_products_endpoint():
    """测试同步产品端点内部逻辑"""
    from fastapi import HTTPException

    from app.api.v1.endpoints.ozon import sync_products
    from app.models.database import Shop, TeamMember, User

    # 创建模拟对象
    mock_db = AsyncMock()
    mock_current_user = MagicMock(spec=User)
    mock_current_user.id = "test-user-id"

    # 模拟TeamMember查询
    mock_member = MagicMock(spec=TeamMember)
    mock_member.team_id = "test-team-id"

    # 模拟Shop查询
    mock_shop = MagicMock(spec=Shop)
    mock_shop.id = "test-shop-id"
    mock_shop.api_credentials = {
        "client_id": "2867211",
        "api_key": "6d13a910-3e64-4954-bd70-3b46e9f38841",
    }
    mock_shop.team_id = "test-team-id"

    # 设置模拟返回值
    async def mock_execute(query):
        # 根据查询返回不同的结果
        # 简化：检查查询类型
        return MagicMock(
            scalar_one_or_none=AsyncMock(return_value=mock_member),
            scalars=MagicMock(
                return_value=MagicMock(first=AsyncMock(return_value=mock_shop))
            ),
        )

    mock_db.execute = mock_execute

    # 模拟OzonIntegrationAdapter
    mock_adapter = AsyncMock()
    mock_adapter.sync_products_to_database = AsyncMock(
        return_value={"synced": 10, "updated": 5, "total": 15, "message": "同步成功"}
    )

    # 模拟OzonIntegrationAdapter构造函数
    with patch(
        "app.api.v1.endpoints.ozon.OzonIntegrationAdapter", return_value=mock_adapter
    ):
        # 模拟异步上下文管理器
        mock_adapter.__aenter__ = AsyncMock(return_value=mock_adapter)
        mock_adapter.__aexit__ = AsyncMock(return_value=None)

        try:
            # 调用端点函数
            result = await sync_products(
                shop_id=None, current_user=mock_current_user, db=mock_db
            )
            print(f"SUCCESS: Endpoint returned: {result}")
            print(f"Result type: {type(result)}")
            return True
        except HTTPException as e:
            print(f"HTTPException: status={e.status_code}, detail={e.detail}")
            return False
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_sync_products_endpoint())
    sys.exit(0 if success else 1)
