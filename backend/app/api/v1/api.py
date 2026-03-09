from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    customers,
    inventory,
    orders,
    ozon,
    products,
    shops,
    teams,
    users,
    selection,
    dropship,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(ozon.router, prefix="/ozon", tags=["ozon"])
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["Operations Dashboard"]
)
api_router.include_router(
    selection.router, prefix="/selection", tags=["Selection Management"]
)
api_router.include_router(dropship.router, prefix="/dropship", tags=["Dropship Orders"])
