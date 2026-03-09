# -*- coding: utf-8 -*-
"""
iCross Automation Service
Implements complete flow from selection to listing to dropship
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import sys
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os

os.environ["DATABASE_TYPE"] = "sqlite"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Product, ProductVariant, PlatformProduct, Shop
from app.models.dropshipping import Supplier, ProductSupplierLink, DropshipOrder
from app.services.spu_utils import extract_spu
from app.integrations.ozon.adapter import OzonIntegrationAdapter

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


class AutomationService:
    """Automation service"""

    def __init__(self, team_id: str = "default-team"):
        self.team_id = team_id
        self.session = Session()

    def close(self):
        self.session.close()

    # ==================== Selection Management ====================

    def get_products_by_selection_status(self, status: str) -> List[Product]:
        """Get products by selection status"""
        return (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, selection_status=status)
            .all()
        )

    def get_selected_products(self) -> List[Product]:
        """Get selected products (pending listing)"""
        return self.get_products_by_selection_status("selected")

    def get_draft_products(self) -> List[Product]:
        """Get draft products"""
        return self.get_products_by_selection_status("draft")

    def mark_product_selected(
        self,
        product_id: str,
        source_url: str,
        source_price: float,
        source_supplier: str = "",
    ) -> bool:
        """Mark product as selected"""
        product = self.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return False

        product.selection_status = "selected"
        product.source_url = source_url
        product.source_price = source_price
        product.source_supplier = source_supplier
        product.updated_at = datetime.utcnow()

        self.session.commit()
        return True

    def import_selected_products(self, products_data: List[Dict]) -> Dict[str, int]:
        """Import selected products from Excel"""
        imported = 0
        skipped = 0

        processed_spus = set()

        for item in products_data:
            sku = item.get("sku", "")
            if not sku:
                skipped += 1
                continue

            spu = extract_spu(sku)

            # Import each SPU only once
            if spu in processed_spus:
                continue

            # Check if already exists
            existing = self.session.query(Product).filter_by(master_sku=spu).first()
            if existing:
                skipped += 1
                continue

            # Extract purchase cost
            purchase_cost = item.get("purchase_cost", 0)
            try:
                purchase_cost = float(purchase_cost) if purchase_cost else 0
            except:
                purchase_cost = 0

            # 1688 link
            source_url = item.get("1688_link", "")
            if not source_url or str(source_url) == "nan":
                # Get from extra_data
                source_url = ""

            city = item.get("city", "")

            # Create product
            product = Product(
                id=f"prod-{spu.replace('#', '').replace('-', '')[:20]}",
                team_id=self.team_id,
                master_sku=spu,
                title=item.get("ozon_name", item.get("1688_name", "Unknown Product"))[
                    :255
                ]
                or "Unknown Product",
                description="",
                selection_status="selected",  # Selected
                listing_status="not_listed",  # Not listed
                source_url=source_url,
                source_price=purchase_cost,
                source_supplier=city if city else "Default Supplier",
                extra_data={
                    "1688_name": item.get("1688_name", ""),
                    "category": item.get("category", ""),
                },
            )

            self.session.add(product)
            imported += 1
            processed_spus.add(spu)

        self.session.commit()

        return {"imported": imported, "skipped": skipped}

    # ==================== Listing Management ====================

    def get_products_by_listing_status(self, status: str) -> List[Product]:
        """Get products by listing status"""
        return (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, listing_status=status)
            .all()
        )

    def get_listed_products(self) -> List[Product]:
        """Get listed products"""
        return self.get_products_by_listing_status("listed")

    def get_pending_products(self) -> List[Product]:
        """Get pending listing products"""
        return self.get_products_by_listing_status("pending")

    def update_product_listing_status(self, product_id: str, status: str) -> bool:
        """Update product listing status"""
        product = self.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return False

        product.listing_status = status
        product.updated_at = datetime.utcnow()
        self.session.commit()
        return True

    # ==================== Ozon Listing ====================

    def list_product_on_ozon(self, product_id: str) -> Dict[str, Any]:
        """List product on Ozon"""
        product = self.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return {"success": False, "error": "Product not found"}

        if product.listing_status == "listed":
            return {"success": False, "error": "Product already listed"}

        # Get shop
        shop = self.session.query(Shop).filter_by(platform="ozon").first()
        if not shop:
            return {"success": False, "error": "Ozon shop not configured"}

        # Get variants
        variants = (
            self.session.query(ProductVariant).filter_by(product_id=product_id).all()
        )
        if not variants:
            return {"success": False, "error": "Product has no variants"}

        # Mock listing (actual needs to call Ozon API)
        # Mark as listed for now
        product.listing_status = "listed"
        product.updated_at = datetime.utcnow()

        # Create PlatformProduct for each variant
        for variant in variants:
            # Check if already exists
            existing_pp = (
                self.session.query(PlatformProduct)
                .filter_by(variant_id=variant.id, shop_id=shop.id)
                .first()
            )

            if not existing_pp:
                platform_product = PlatformProduct(
                    id=f"pp-{variant.id}",
                    product_id=product_id,
                    variant_id=variant.id,
                    shop_id=shop.id,
                    platform_product_id=f"ozon-{variant.id[:8]}",
                    platform_sku=variant.sku,
                    platform_title=product.title,
                    platform_price=variant.price or 0,
                    platform_stock=100,  # Default stock
                    platform_status="active",
                    platform_url=f"https://www.ozon.ru/product/{variant.id[:8]}",
                    last_synced_at=datetime.utcnow(),
                    sync_status="synced",
                )
                self.session.add(platform_product)

        self.session.commit()

        return {
            "success": True,
            "product_id": product_id,
            "spu": product.master_sku,
            "variants_count": len(variants),
        }

    def auto_list_all_selected(self) -> Dict[str, Any]:
        """Auto list all selected products"""
        products = self.get_selected_products()

        success_count = 0
        failed_count = 0
        results = []

        for product in products:
            result = self.list_product_on_ozon(product.id)
            if result.get("success"):
                success_count += 1
            else:
                failed_count += 1
            results.append(
                {"product_id": product.id, "spu": product.master_sku, "result": result}
            )

        return {
            "total": len(products),
            "success": success_count,
            "failed": failed_count,
            "results": results,
        }

    # ==================== Dropship Orders ====================

    def create_dropship_order(
        self, sku: str, quantity: int = 1, sale_price: float = 0
    ) -> Optional[DropshipOrder]:
        """Create dropship order"""
        # Find product
        variant = self.session.query(ProductVariant).filter_by(sku=sku).first()
        if not variant:
            logger.warning(f"Variant not found: {sku}")
            return None

        product = variant.product
        shop = self.session.query(Shop).filter_by(platform="ozon").first()

        # Find supplier
        spu = extract_spu(sku)
        supplier_link = (
            self.session.query(ProductSupplierLink)
            .filter_by(spu=spu, is_active=True)
            .first()
        )

        if not supplier_link:
            logger.warning(f"Supplier link not found for SPU: {spu}")
            return None

        supplier = supplier_link.supplier

        # Calculate cost
        purchase_cost = supplier_link.purchase_cost or 0
        shipping_cost = supplier_link.shipping_cost or 0
        total_cost = (purchase_cost + shipping_cost) * quantity
        profit = sale_price - total_cost

        # Create dropship order
        dropship_order = DropshipOrder(
            id=f"do-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            team_id=self.team_id,
            shop_id=shop.id if shop else "",
            platform_order_id="",
            product_id=product.id,
            variant_id=variant.id,
            sku=sku,
            quantity=quantity,
            supplier_id=supplier.id if supplier else None,
            purchase_cost=purchase_cost,
            shipping_cost=shipping_cost,
            total_cost=total_cost,
            sale_price=sale_price,
            profit=profit,
            status="pending",
            auto_dropship=True,
            order_placed_at=datetime.utcnow(),
        )

        self.session.add(dropship_order)
        self.session.commit()

        return dropship_order

    # ==================== Statistics ====================

    def get_selection_stats(self) -> Dict[str, int]:
        """Get selection stats"""
        total = self.session.query(Product).filter_by(team_id=self.team_id).count()
        draft = (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, selection_status="draft")
            .count()
        )
        selected = (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, selection_status="selected")
            .count()
        )

        return {
            "total": total,
            "draft": draft,
            "selected": selected,
        }

    def get_listing_stats(self) -> Dict[str, int]:
        """Get listing stats"""
        total = self.session.query(Product).filter_by(team_id=self.team_id).count()
        not_listed = (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, listing_status="not_listed")
            .count()
        )
        pending = (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, listing_status="pending")
            .count()
        )
        listed = (
            self.session.query(Product)
            .filter_by(team_id=self.team_id, listing_status="listed")
            .count()
        )

        return {
            "total": total,
            "not_listed": not_listed,
            "pending": pending,
            "listed": listed,
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """Get operations dashboard"""
        return {
            "selection": self.get_selection_stats(),
            "listing": self.get_listing_stats(),
            "dropship_orders": self.session.query(DropshipOrder)
            .filter_by(team_id=self.team_id)
            .count(),
        }


def create_automation_service(team_id: str = "default-team") -> AutomationService:
    """Create automation service instance"""
    return AutomationService(team_id)


if __name__ == "__main__":
    service = create_automation_service()

    print("=== iCross Automation Dashboard ===\n")

    dashboard = service.get_dashboard()

    print("Selection Status:")
    for k, v in dashboard["selection"].items():
        print(f"  {k}: {v}")

    print("\nListing Status:")
    for k, v in dashboard["listing"].items():
        print(f"  {k}: {v}")

    print(f"\nDropship Orders: {dashboard['dropship_orders']}")

    service.close()
