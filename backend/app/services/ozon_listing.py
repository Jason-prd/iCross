# -*- coding: utf-8 -*-
"""
Ozon API Listing Service
Implements actual product listing to Ozon
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os

os.environ["DATABASE_TYPE"] = "sqlite"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Product, ProductVariant, PlatformProduct, Shop
from app.integrations.ozon.adapter import OzonIntegrationAdapter

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


class OzonListingService:
    """Ozon listing service"""

    def __init__(self, team_id: str = "default-team"):
        self.team_id = team_id
        self.session = Session()

    def close(self):
        self.session.close()

    def get_shop(self) -> Optional[Shop]:
        """Get Ozon shop"""
        return self.session.query(Shop).filter_by(platform="ozon").first()

    def get_ozon_adapter(self) -> Optional[OzonIntegrationAdapter]:
        """Get Ozon adapter"""
        shop = self.get_shop()
        if not shop:
            return None

        credentials = shop.api_credentials
        client_id = credentials.get("client_id")
        api_key = credentials.get("api_key")

        if not client_id or not api_key:
            return None

        return OzonIntegrationAdapter(client_id=client_id, api_key=api_key)

    def prepare_product_for_ozon(
        self, product: Product, variants: List[ProductVariant]
    ) -> Dict[str, Any]:
        """Prepare product data for Ozon listing"""

        # Prepare product attributes
        items = []

        for variant in variants:
            # Calculate price (simple pricing formula)
            base_cost = variant.cost or 0
            # Pricing: (cost x exchange rate 13) x (1 + shipping + commission 12% + fee 2% + profit 35%)
            # Simplified: cost x 2.5
            price = base_cost * 2.5

            item = {
                "offer_id": variant.sku,
                "name": product.title[:255],
                "price": price,
                "stock": variant.inventory[0].quantity if variant.inventory else 100,
                "sku": variant.sku,
            }
            items.append(item)

        return {
            "product_id": product.id,
            "spu": product.master_sku,
            "title": product.title,
            "items": items,
            "category_id": None,  # Need to get from Ozon category
        }

    async def list_product_async(self, product_id: str) -> Dict[str, Any]:
        """Async list product on Ozon"""

        # Get product
        product = self.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return {"success": False, "error": "Product not found"}

        # Get variants
        variants = (
            self.session.query(ProductVariant).filter_by(product_id=product_id).all()
        )
        if not variants:
            return {"success": False, "error": "No variants"}

        # Get adapter
        adapter = self.get_ozon_adapter()
        if not adapter:
            return {"success": False, "error": "Ozon not configured"}

        try:
            async with adapter:
                # Prepare product data
                prepared = self.prepare_product_for_ozon(product, variants)

                # Call Ozon API to create product
                # Simplified for now, actual needs to follow Ozon API docs
                result = await adapter.create_product_from_dict(prepared)

                # Update local status
                product.listing_status = "listed"
                product.updated_at = datetime.utcnow()

                # Update PlatformProduct
                shop = self.get_shop()
                for variant in variants:
                    pp = (
                        self.session.query(PlatformProduct)
                        .filter_by(variant_id=variant.id, shop_id=shop.id)
                        .first()
                    )

                    if pp:
                        pp.platform_status = "active"
                        pp.last_synced_at = datetime.utcnow()

                self.session.commit()

                return {
                    "success": True,
                    "product_id": product_id,
                    "spu": product.master_sku,
                    "variants_count": len(variants),
                }

        except Exception as e:
            logger.error(f"Failed to list product: {e}")
            return {"success": False, "error": str(e)}

    def list_product(self, product_id: str) -> Dict[str, Any]:
        """Sync list product"""
        return asyncio.run(self.list_product_async(product_id))

    async def list_products_batch_async(self, product_ids: List[str]) -> Dict[str, Any]:
        """Batch list products"""

        results = {"success": 0, "failed": 0, "errors": []}

        for product_id in product_ids:
            result = await self.list_product_async(product_id)
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(
                    {"product_id": product_id, "error": result.get("error")}
                )

        return results

    def list_products_batch(self, product_ids: List[str]) -> Dict[str, Any]:
        """Sync batch list"""
        return asyncio.run(self.list_products_batch_async(product_ids))

    def get_category_tree(self) -> List[Dict]:
        """Get Ozon category tree"""
        adapter = self.get_ozon_adapter()
        if not adapter:
            return []

        categories = []

        async def fetch():
            nonlocal categories
            try:
                async with adapter:
                    categories = await adapter.get_category_tree()
            except Exception as e:
                logger.error(f"Failed to get category tree: {e}")

        asyncio.run(fetch())
        return categories


def create_ozon_listing_service(team_id: str = "default-team") -> OzonListingService:
    """Create Ozon listing service"""
    return OzonListingService(team_id)


if __name__ == "__main__":
    service = create_ozon_listing_service()

    # Test connection
    shop = service.get_shop()
    print(f"Shop: {shop.name if shop else 'Not found'}")

    adapter = service.get_ozon_adapter()
    print(f"Ozon Adapter: {'OK' if adapter else 'Failed'}")

    service.close()
