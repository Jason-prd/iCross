import asyncio

from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.database import Shop


async def test_shop_query():
    async with async_session_maker() as session:
        # 模拟ozon.py中的查询
        result = await session.execute(select(Shop).where(Shop.platform == "ozon"))

        print("Testing result.first():")
        shop_row = result.first()
        print(f"Type of result.first(): {type(shop_row)}")
        print(f"Value of result.first(): {shop_row}")

        if shop_row:
            print(f"First element type: {type(shop_row[0])}")
            print(f"First element: {shop_row[0]}")
            print(
                f"Has api_credentials attr: {hasattr(shop_row[0], 'api_credentials')}"
            )
            if hasattr(shop_row[0], "api_credentials"):
                print(f"api_credentials: {shop_row[0].api_credentials}")
                print(f"api_credentials type: {type(shop_row[0].api_credentials)}")

        print("\nTesting result.scalars().first():")
        result2 = await session.execute(select(Shop).where(Shop.platform == "ozon"))
        shop_obj = result2.scalars().first()
        print(f"Type: {type(shop_obj)}")
        print(f"Value: {shop_obj}")
        if shop_obj:
            print(f"api_credentials: {shop_obj.api_credentials}")
            print(f"api_credentials type: {type(shop_obj.api_credentials)}")


if __name__ == "__main__":
    asyncio.run(test_shop_query())
