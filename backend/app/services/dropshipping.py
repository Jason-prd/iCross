# -*- coding: utf-8 -*-
"""
iCross One-Click Dropship Service (SPU Level)
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os

os.environ["DATABASE_TYPE"] = "sqlite"

import math
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Product, ProductVariant, PlatformProduct, Shop
from app.models.dropshipping import (
    Supplier,
    ProductSupplierLink,
    DropshipOrder,
    DropshipSettings,
)
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.services.spu_utils import extract_spu

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./icross_dev.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


def safe_float(value, default=0):
    """Safely convert to float"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        if math.isnan(value) or math.isinf(value):
            return default
        return float(value)
    if isinstance(value, str):
        if value.lower() in ["nan", "none", "null", ""]:
            return default
        try:
            return float(value)
        except:
            return default
    try:
        return float(value)
    except:
        return default


def safe_str(value, default=""):
    """Safely convert to string"""
    if value is None:
        return default
    if isinstance(value, str):
        if value.lower() in ["nan", "none", "null", ""]:
            return default
        return value
    return str(value)


class DropshippingService:
    """Dropship service (SPU level)"""

    def __init__(self, team_id: str = "default-team"):
        self.team_id = team_id
        self.session = Session()

    def close(self):
        self.session.close()

    def get_settings(self) -> DropshipSettings:
        settings = (
            self.session.query(DropshipSettings).filter_by(team_id=self.team_id).first()
        )
        if not settings:
            settings = DropshipSettings(
                id=f"settings-{self.team_id}",
                team_id=self.team_id,
                auto_dropship_enabled=False,
                order_sync_interval=5,
                inventory_sync_interval=30,
                low_stock_threshold=10,
                price_change_threshold=20,
            )
            self.session.add(settings)
            self.session.commit()
        return settings

    def get_shop(self) -> Optional[Shop]:
        return self.session.query(Shop).filter_by(platform="ozon").first()

    def get_spu_link(self, sku: str) -> Optional[ProductSupplierLink]:
        spu = extract_spu(sku)

        link = (
            self.session.query(ProductSupplierLink)
            .filter(
                ProductSupplierLink.spu == spu,
                ProductSupplierLink.is_active == True,
                ProductSupplierLink.is_preferred == True,
            )
            .first()
        )

        if not link:
            link = (
                self.session.query(ProductSupplierLink)
                .filter(
                    ProductSupplierLink.spu == spu,
                    ProductSupplierLink.is_active == True,
                )
                .first()
            )

        return link

    def get_product_info(self, sku: str) -> Optional[Dict[str, Any]]:
        variant = self.session.query(ProductVariant).filter_by(sku=sku).first()
        if not variant:
            return None

        product = variant.product
        platform_product = (
            self.session.query(PlatformProduct).filter_by(variant_id=variant.id).first()
        )

        info = {
            "sku": sku,
            "spu": extract_spu(sku),
            "product_id": product.id,
            "variant_id": variant.id,
            "title": product.title,
            "price": variant.price,
            "cost": variant.cost,
            "ozon_product_id": platform_product.platform_product_id
            if platform_product
            else None,
            "ozon_stock": platform_product.platform_stock if platform_product else 0,
            "extra_data": product.extra_data or {},
        }

        link = self.get_spu_link(sku)
        if link:
            info["supplier"] = {
                "id": link.supplier_id,
                "name": link.supplier.name if link.supplier else None,
                "product_url": link.supplier_product_url,
                "purchase_cost": link.purchase_cost,
                "shipping_cost": link.shipping_cost,
                "warehouse": link.warehouse,
                "spu": link.spu,
            }

        return info

    def link_spu_to_supplier(
        self,
        sku: str,
        supplier_id: str,
        supplier_product_url: str,
        purchase_cost: float = 0,
        shipping_cost: float = 0,
        warehouse: str = "",
        is_preferred: bool = True,
    ) -> bool:
        spu = extract_spu(sku)

        variants = (
            self.session.query(ProductVariant)
            .filter(ProductVariant.sku.like(f"SKU#{spu[4:]}%"))
            .all()
        )

        product_id = None
        variant_id = None
        if variants:
            product_id = variants[0].product_id
            variant_id = variants[0].id

        existing_link = (
            self.session.query(ProductSupplierLink)
            .filter_by(spu=spu, supplier_id=supplier_id)
            .first()
        )

        if existing_link:
            existing_link.supplier_product_url = supplier_product_url
            existing_link.purchase_cost = purchase_cost
            existing_link.shipping_cost = shipping_cost
            existing_link.warehouse = warehouse
            existing_link.is_preferred = is_preferred
            existing_link.product_id = product_id
            existing_link.variant_id = variant_id
        else:
            link = ProductSupplierLink(
                id=f"link-{spu.replace('#', '')}-{supplier_id}",
                team_id=self.team_id,
                spu=spu,
                product_id=product_id,
                variant_id=variant_id,
                supplier_id=supplier_id,
                supplier_product_url=supplier_product_url,
                purchase_cost=purchase_cost,
                shipping_cost=shipping_cost,
                warehouse=warehouse,
                is_preferred=is_preferred,
            )
            self.session.add(link)

        self.session.commit()
        return True

    def get_all_spu_links(self) -> List[Dict[str, Any]]:
        links = (
            self.session.query(ProductSupplierLink)
            .filter_by(team_id=self.team_id, is_active=True)
            .all()
        )

        result = []
        for link in links:
            result.append(
                {
                    "spu": link.spu,
                    "supplier": link.supplier.name if link.supplier else None,
                    "product_url": link.supplier_product_url,
                    "purchase_cost": link.purchase_cost,
                    "warehouse": link.warehouse,
                    "is_preferred": link.is_preferred,
                }
            )

        return result

    def get_dashboard_stats(self) -> Dict[str, Any]:
        total_spus = (
            self.session.query(ProductSupplierLink)
            .filter_by(team_id=self.team_id, is_active=True)
            .count()
        )

        total_orders = (
            self.session.query(DropshipOrder).filter_by(team_id=self.team_id).count()
        )
        pending = (
            self.session.query(DropshipOrder)
            .filter_by(team_id=self.team_id, status="pending")
            .count()
        )
        processing = (
            self.session.query(DropshipOrder)
            .filter_by(team_id=self.team_id, status="processing")
            .count()
        )
        shipped = (
            self.session.query(DropshipOrder)
            .filter_by(team_id=self.team_id, status="shipped")
            .count()
        )

        suppliers = self.session.query(Supplier).filter_by(team_id=self.team_id).count()

        return {
            "total_spus_linked": total_spus,
            "total_orders": total_orders,
            "pending_orders": pending,
            "processing_orders": processing,
            "shipped_orders": shipped,
            "total_suppliers": suppliers,
        }

    def import_from_excel(self, products_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        supplier = self.session.query(Supplier).filter_by(team_id=self.team_id).first()
        if not supplier:
            supplier = Supplier(
                id="default-supplier",
                team_id=self.team_id,
                name="Default Supplier",
                platform="1688",
                is_active=True,
            )
            self.session.add(supplier)
            self.session.commit()

        linked_spus = set()
        skipped = 0

        for product_info in products_data:
            sku = safe_str(product_info.get("sku", ""), "")
            if not sku:
                skipped += 1
                continue

            spu = extract_spu(sku)

            if spu in linked_spus:
                continue

            # Safely process values
            purchase_cost = safe_float(product_info.get("purchase_cost", 0))
            shipping_cost = safe_float(product_info.get("shipping_cost", 0))
            warehouse = safe_str(product_info.get("city", ""), "")

            # Get 1688 link
            link_1688 = safe_str(product_info.get("1688_link", ""), "")

            if not link_1688:
                product_info_data = self.get_product_info(sku)
                if product_info_data:
                    extra = product_info_data.get("extra_data", {})
                    link_1688 = safe_str(extra.get("1688_link", ""), "")

            if not link_1688:
                skipped += 1
                continue

            # SPU level link
            success = self.link_spu_to_supplier(
                sku=sku,
                supplier_id=supplier.id,
                supplier_product_url=link_1688,
                purchase_cost=purchase_cost,
                shipping_cost=shipping_cost,
                warehouse=warehouse if warehouse else "Shenzhen",
                is_preferred=True,
            )

            if success:
                linked_spus.add(spu)

        return {
            "spus_linked": len(linked_spus),
            "skipped": skipped,
            "supplier_id": supplier.id,
        }


def create_dropshipping_service(team_id: str = "default-team") -> DropshippingService:
    return DropshippingService(team_id)


if __name__ == "__main__":
    service = DropshippingService()
    stats = service.get_dashboard_stats()
    print("=== Dropshipping Stats (SPU Level) ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    links = service.get_all_spu_links()
    print(f"\n=== SPU Links ({len(links)}) ===")
    for link in links[:5]:
        print(f"  {link}")

    service.close()
