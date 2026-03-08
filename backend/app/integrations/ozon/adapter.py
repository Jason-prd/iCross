"""
Ozon Integration Adapter

Provides high-level interface for interacting with Ozon API,
including data transformation, error handling, and logging.
Uses ozonapi-async library.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, select

try:
    from ozonapi import SellerAPI, SellerAPIConfig
    from ozonapi.seller.core.exceptions import APIError

    OZON_API_AVAILABLE = True
except ImportError:
    OZON_API_AVAILABLE = False
    APIError = Exception
    logger.warning("Ozon API库未找到，请安装 ozonapi-async")

from .config import ozon_config
from .exceptions import (
    OzonAuthenticationError,
    OzonConnectionError,
    OzonIntegrationError,
)
from .models import (
    OzonCategory,
    OzonDeliveryMethod,
    OzonInventoryItem,
    OzonOrder,
    OzonProduct,
    OzonProductPrice,
    OzonProductStock,
    OzonSellerInfo,
    OzonWarehouse,
)


class OzonIntegrationAdapter:
    """Ozon平台集成适配器"""

    def __init__(self, client_id: Optional[str] = None, api_key: Optional[str] = None):
        if not OZON_API_AVAILABLE:
            raise ImportError("Ozon API库不可用，请检查安装")

        self.client_id = client_id or ozon_config.client_id
        self.api_key = api_key or ozon_config.api_key
        self._api: Optional[SellerAPI] = None
        self._connected = False

        client_id_display = self.client_id[:10] if self.client_id else "未配置"
        logger.info(f"初始化Ozon集成适配器，客户端ID: {client_id_display}...")

    async def connect(self) -> bool:
        """连接到Ozon API"""
        try:
            if not self.client_id or not self.api_key:
                raise OzonAuthenticationError("Ozon API凭证未配置")

            self._api = SellerAPI(
                client_id=self.client_id,
                api_key=self.api_key,
            )

            self._connected = True
            logger.info("Ozon API适配器已初始化")
            return True

        except APIError as e:
            logger.error(f"初始化Ozon API失败: {e}")
            raise OzonConnectionError(f"初始化失败: {e}")
        except Exception as e:
            logger.error(f"初始化Ozon API时发生未知错误: {type(e).__name__}: {str(e)}")
            error_msg = str(e) if str(e) else f"{type(e).__name__} (no message)"
            raise OzonConnectionError(f"初始化错误: {error_msg}")

    async def disconnect(self):
        """断开Ozon API连接"""
        self._connected = False
        self._api = None
        logger.info("已断开Ozon API连接")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    def _ensure_connected(self):
        """确保已连接到Ozon API"""
        if not self._connected or not self._api:
            raise OzonConnectionError("未连接到Ozon API，请先调用connect()方法")

    async def get_products(
        self, page: int = 1, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[OzonProduct]:
        """获取Ozon商品列表"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.products.v3__product_list import (
                ProductListFilter,
                ProductListRequest,
            )

            filter_obj = ProductListFilter(visibility="ALL")

            request = ProductListRequest(
                filter=filter_obj,
                limit=limit,
            )

            response = await self._api.product_list(request)

            products = []
            if (
                hasattr(response, "result")
                and response.result
                and hasattr(response.result, "items")
            ):
                for item in response.result.items:
                    item_dict = (
                        item.model_dump() if hasattr(item, "model_dump") else item
                    )
                    product = OzonProduct(
                        product_id=item_dict.get("id") or item_dict.get("product_id"),
                        offer_id=item_dict.get("offer_id", ""),
                        name=item_dict.get("name", ""),
                        sku=item_dict.get("offer_id", ""),
                        price=float(item_dict.get("price", 0) or 0),
                        quantity=item_dict.get("stock", 0) or 0,
                        visibility=item_dict.get("visibility", "INVISIBLE"),
                        category_id=item_dict.get("category_id"),
                        created_at=self._parse_datetime(item_dict.get("created_at")),
                        updated_at=self._parse_datetime(item_dict.get("updated_at")),
                        images=item_dict.get("images", []) or [],
                        attributes=item_dict.get("attributes")
                        if isinstance(item_dict.get("attributes"), list)
                        else [],
                        raw_data=item_dict,
                    )
                    products.append(product)

            logger.info(f"成功获取{len(products)}个Ozon商品")
            return products

        except APIError as e:
            logger.error(f"获取Ozon商品列表失败: {e}")
            raise OzonIntegrationError(f"获取商品失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon商品列表时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取商品错误: {str(e)}")

    async def create_product(self, product: OzonProduct) -> Dict[str, Any]:
        """在Ozon创建商品"""
        self._ensure_connected()

        try:
            items = [
                {
                    "offer_id": product.offer_id,
                    "name": product.name,
                    "price": str(product.price),
                }
            ]
            result = await self._api.product_import(items=items)

            logger.info(f"成功创建Ozon商品")
            return {
                "result": result.model_dump()
                if hasattr(result, "model_dump")
                else result
            }

        except APIError as e:
            logger.error(f"创建Ozon商品失败: {e}")
            raise OzonIntegrationError(f"创建商品失败: {e}")
        except Exception as e:
            logger.error(f"创建Ozon商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"创建商品错误: {str(e)}")

    async def update_product(self, product: OzonProduct) -> Dict[str, Any]:
        """在Ozon更新商品信息"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import ProductImportRequest, ProductImportItem

            # Try to get type_id from product info, fallback to category_id
            type_id = product.category_id or 17027929
            try:
                if product.product_id:
                    details = await self.get_product_details([product.product_id])
                    if details and len(details) > 0:
                        type_id = details[0].get("type_id", 0) or type_id
            except Exception:
                pass

            # Determine valid VAT value (must be exact format: 0, 0.05, 0.07, 0.10, 0.20, 0.22)
            vat_value = "0.10"
            if product.vat is not None:
                try:
                    vat_float = float(product.vat)
                    # Round to valid VAT values
                    if vat_float <= 0:
                        vat_value = "0"
                    elif vat_float <= 0.05:
                        vat_value = "0.05"
                    elif vat_float <= 0.07:
                        vat_value = "0.07"
                    elif vat_float <= 0.10:
                        vat_value = "0.10"
                    elif vat_float <= 0.20:
                        vat_value = "0.20"
                    else:
                        vat_value = "0.22"
                except (ValueError, TypeError):
                    vat_str = str(product.vat).strip()
                    vat_map = {
                        "0": "0",
                        "0.0": "0",
                        "0.00": "0",
                        "0.05": "0.05",
                        "5": "0.05",
                        "0.5": "0.05",
                        "0.07": "0.07",
                        "7": "0.07",
                        "0.7": "0.07",
                        "0.1": "0.10",
                        "0.10": "0.10",
                        "1": "0.10",
                        "10": "0.10",
                        "0.2": "0.20",
                        "0.20": "0.20",
                        "2": "0.20",
                        "20": "0.20",
                        "0.22": "0.22",
                        "22": "0.22",
                    }
                    vat_value = vat_map.get(vat_str, "0.10")

            item_kwargs = {
                "offer_id": product.offer_id,
                "name": product.name[:500] if product.name else "",
                "description_category_id": product.category_id or 17027929,
                "new_description_category_id": 0,
                "type_id": type_id,
                "depth": int(product.depth) if product.depth else 10,
                "width": int(product.width) if product.width else 10,
                "dimension_unit": product.dimension_unit or "mm",
                "height": int(product.height) if product.height else 10,
                "weight": int(product.weight) if product.weight else 100,
                "weight_unit": product.weight_unit or "g",
                "price": str(int(product.price)) if product.price else "0",
                "vat": vat_value,
            }

            if product.old_price is not None:
                item_kwargs["old_price"] = str(int(product.old_price))

            if product.category_id is not None:
                item_kwargs["description_category_id"] = product.category_id

            if product.barcode is not None:
                item_kwargs["barcode"] = product.barcode

            if product.images and len(product.images) > 0:
                item_kwargs["images"] = product.images

            if product.images360 and len(product.images360) > 0:
                item_kwargs["images360"] = product.images360

            if product.color_image is not None:
                item_kwargs["color_image"] = product.color_image

            if product.attributes and len(product.attributes) > 0:
                item_kwargs["attributes"] = product.attributes

            item = ProductImportItem(**item_kwargs)
            request = ProductImportRequest(items=[item])

            logger.info(f"Calling product_import with request: {request.model_dump()}")
            import_result = await self._api.product_import(request=request)

            # 获取task_id
            task_id = None
            if hasattr(import_result, "result") and hasattr(
                import_result.result, "task_id"
            ):
                task_id = import_result.result.task_id

            if not task_id:
                logger.warning(f"product_import未返回task_id: {import_result}")
                return {
                    "result": import_result.model_dump()
                    if hasattr(import_result, "model_dump")
                    else import_result
                }

            # 等待一下再查询结果（Ozon处理需要时间）
            import asyncio

            await asyncio.sleep(2)

            # 查询导入结果
            from ozonapi.seller.schemas.products import ProductImportInfoRequest

            info_request = ProductImportInfoRequest(task_id=task_id)
            info_result = await self._api.product_import_info(request=info_request)

            # 检查是否有错误
            if hasattr(info_result, "result") and info_result.result:
                items = (
                    info_result.result.items
                    if hasattr(info_result.result, "items")
                    else []
                )
                total = (
                    info_result.result.total
                    if hasattr(info_result.result, "total")
                    else 0
                )

                logger.info(f"商品导入任务 {task_id} 处理完成，共 {total} 个商品")

                # 检查每个商品的状态
                errors = []
                for item in items:
                    status = item.status if hasattr(item, "status") else "unknown"
                    offer_id = item.offer_id if hasattr(item, "offer_id") else "unknown"

                    if hasattr(item, "errors") and item.errors:
                        for err in item.errors:
                            err_msg = f"商品 {offer_id}: {err.description if hasattr(err, 'description') else err.message if hasattr(err, 'message') else str(err)}"
                            errors.append(err_msg)
                            logger.error(f"商品导入错误: {err_msg}")

                    logger.info(f"商品 {offer_id} 状态: {status}")

                if errors:
                    error_summary = "; ".join(errors[:5])  # 最多显示5个错误
                    raise OzonIntegrationError(f"商品导入存在问题: {error_summary}")

            logger.info(f"成功更新Ozon商品: {product.offer_id}")
            return {
                "task_id": task_id,
                "result": import_result.model_dump()
                if hasattr(import_result, "model_dump")
                else import_result,
            }

        except APIError as e:
            logger.error(f"更新Ozon商品失败: {e}")
            raise OzonIntegrationError(f"更新商品失败: {e}")
        except Exception as e:
            logger.error(f"更新Ozon商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"更新商品错误: {str(e)}")

    async def archive_product(self, product_id: int) -> Dict[str, Any]:
        """在Ozon归档商品"""
        self._ensure_connected()

        try:
            result = await self._api.product_archive(product_id=[product_id])
            logger.info(f"成功归档Ozon商品，product_id: {product_id}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"归档Ozon商品失败: {e}")
            raise OzonIntegrationError(f"归档商品失败: {e}")
        except Exception as e:
            logger.error(f"归档Ozon商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"归档商品错误: {str(e)}")

    async def unarchive_product(self, product_id: int) -> Dict[str, Any]:
        """在Ozon取消归档商品"""
        self._ensure_connected()

        try:
            result = await self._api.product_unarchive(product_id=[product_id])
            logger.info(f"成功取消归档Ozon商品，product_id: {product_id}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"取消归档Ozon商品失败: {e}")
            raise OzonIntegrationError(f"取消归档商品失败: {e}")
        except Exception as e:
            logger.error(f"取消归档Ozon商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"取消归档商品错误: {str(e)}")

    async def get_categories(self) -> List[OzonCategory]:
        """获取Ozon分类树"""
        self._ensure_connected()

        try:
            result = await self._api.description_category_tree()

            categories = []
            if hasattr(result, "result") and result.result:
                for cat in result.result:
                    cat_dict = (
                        cat
                        if isinstance(cat, dict)
                        else cat.model_dump()
                        if hasattr(cat, "model_dump")
                        else {}
                    )
                    categories.append(
                        OzonCategory(
                            id=cat_dict.get("category_id", 0),
                            name=cat_dict.get("title", ""),
                            parent_id=cat_dict.get("parent_id"),
                            has_children=cat_dict.get("has_children", False),
                            description=cat_dict.get("description", ""),
                            raw_data=cat_dict,
                        )
                    )

            logger.info(f"成功获取{len(categories)}个Ozon分类")
            return categories

        except APIError as e:
            logger.error(f"获取Ozon分类失败: {e}")
            raise OzonIntegrationError(f"获取分类失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon分类时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取分类错误: {str(e)}")

    async def get_fbo_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取Ozon FBO订单列表"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.fbo.v2__posting_fbo_list import (
                PostingFBOListRequest,
            )
            from ozonapi.seller.schemas.entities.postings.filter import PostingFilter

            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()

            filter_data = PostingFilter(
                since=start_date,
                to=end_date,
            )

            request = PostingFBOListRequest(
                filter=filter_data,
                limit=limit,
            )

            response = await self._api.posting_fbo_list(request)

            orders = []
            if hasattr(response, "result") and response.result:
                for order_data in response.result:
                    parsed_order = self._parse_fbo_order(order_data)
                    orders.append(parsed_order)

            logger.info(f"成功获取{len(orders)}个Ozon FBO订单")
            return orders

        except APIError as e:
            logger.error(f"获取Ozon FBO订单失败: {e}")
            raise OzonIntegrationError(f"获取FBO订单失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon FBO订单时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取FBO订单错误: {str(e)}")

    async def get_fbs_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取Ozon FBS订单列表"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.fbs.v3__posting_fbs_list import (
                PostingFBSListRequest,
                PostingFBSListFilter,
            )

            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()

            filter_obj = PostingFBSListFilter(
                since=start_date,
                to=end_date,
            )

            request = PostingFBSListRequest(
                filter=filter_obj,
                limit=limit,
            )

            response = await self._api.posting_fbs_list(request)

            orders = []
            if (
                hasattr(response, "result")
                and response.result
                and hasattr(response.result, "postings")
            ):
                for order_data in response.result.postings:
                    parsed_order = self._parse_fbs_order(order_data)
                    orders.append(parsed_order)

            logger.info(f"成功获取{len(orders)}个Ozon FBS订单")
            return orders

        except APIError as e:
            logger.warning(f"获取Ozon FBS订单失败: {e}")
            return []
        except Exception as e:
            logger.warning(f"获取Ozon FBS订单时发生错误: {str(e)}")
            return []

    async def get_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> List[OzonOrder]:
        """获取Ozon订单列表（合并FBO和FBS）"""
        fbo_orders_data = []
        fbs_orders_data = []

        try:
            fbo_orders_data = await self.get_fbo_orders(start_date, end_date, status)
            logger.info(f"成功获取{len(fbo_orders_data)}个FBO订单")
        except Exception as e:
            logger.error(f"获取FBO订单失败: {str(e)}")

        try:
            fbs_orders_data = await self.get_fbs_orders(start_date, end_date, status)
            logger.info(f"成功获取{len(fbs_orders_data)}个FBS订单")
        except Exception as e:
            logger.error(f"获取FBS订单失败: {str(e)}")

        all_orders = []
        for order_data in fbo_orders_data + fbs_orders_data:
            order = OzonOrder(
                order_id=order_data.get("order_id", ""),
                order_number=order_data.get("order_number", ""),
                status=order_data.get("status", ""),
                customer_name=order_data.get("customer_name"),
                customer_email=order_data.get("customer_email"),
                total_amount=order_data.get("total_amount", 0.0),
                currency=order_data.get("currency", "RUB"),
                created_at=order_data.get("created_at"),
                updated_at=order_data.get("updated_at"),
                items=order_data.get("items", []),
                shipping_address=order_data.get("shipping_address"),
                raw_data=order_data,
            )
            all_orders.append(order)

        logger.info(f"总计获取{len(all_orders)}个Ozon订单")
        return all_orders

    async def get_inventory(self) -> List[OzonInventoryItem]:
        """获取Ozon库存信息"""
        logger.warning("库存API功能待实现")
        return []

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not dt_str:
            return None

        try:
            for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    async def test_connection(self) -> Dict[str, Any]:
        """测试Ozon API连接"""
        try:
            connected = await self.connect()

            if connected:
                categories = await self.get_categories()
                products = await self.get_products(limit=5)

                return {
                    "connected": True,
                    "categories_count": len(categories),
                    "products_count": len(products),
                    "message": "Ozon API连接正常",
                }
            else:
                return {"connected": False, "message": "无法连接到Ozon API"}

        except Exception as e:
            return {"connected": False, "message": f"连接测试失败: {str(e)}"}
        finally:
            await self.disconnect()

    async def get_product_details(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """获取Ozon商品详细信息"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.products.v3__product_info_list import (
                ProductInfoListRequest,
            )

            request = ProductInfoListRequest(
                product_id=product_ids,
            )

            result = await self._api.product_info_list(request)

            results = []
            if hasattr(result, "items") and result.items:
                for item in result.items:
                    item_dict = (
                        item.model_dump() if hasattr(item, "model_dump") else item
                    )
                    results.append(item_dict)

            logger.info(f"成功获取{len(results)}个Ozon商品详情")
            return results

        except APIError as e:
            logger.error(f"获取Ozon商品详情失败: {e}")
            raise OzonIntegrationError(f"获取商品详情失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon商品详情时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取商品详情错误: {str(e)}")

    def _parse_fbo_order(self, order_data: Any) -> Dict[str, Any]:
        """解析Ozon FBO订单数据"""
        try:
            order_dict = (
                order_data.model_dump()
                if hasattr(order_data, "model_dump")
                else order_data
            )
            if not isinstance(order_dict, dict):
                order_dict = {}

            items = []
            products = order_dict.get("products", [])
            for item in products:
                items.append(
                    {
                        "product_id": item.get("product_id"),
                        "offer_id": item.get("offer_id"),
                        "name": item.get("name"),
                        "quantity": item.get("quantity", 1),
                        "price": float(item.get("price", 0)),
                        "sku": item.get("sku"),
                    }
                )

            shipping_address = order_dict.get("delivery_address", {})
            if shipping_address:
                shipping_address = {
                    "address": shipping_address.get("address", ""),
                    "city": shipping_address.get("city", ""),
                    "region": shipping_address.get("region", ""),
                    "postal_code": shipping_address.get("postal_code", ""),
                    "country": shipping_address.get("country", ""),
                    "recipient": shipping_address.get("recipient", {}),
                }

            created_at = self._parse_datetime(order_dict.get("created_at"))
            updated_at = self._parse_datetime(order_dict.get("updated_at"))
            return {
                "order_id": order_dict.get("posting_number", ""),
                "order_number": order_dict.get(
                    "order_number", order_dict.get("posting_number", "")
                ),
                "status": order_dict.get("status", ""),
                "customer_name": order_dict.get("customer", {}).get("name")
                if isinstance(order_dict.get("customer"), dict)
                else None,
                "customer_email": order_dict.get("customer", {}).get("email")
                if isinstance(order_dict.get("customer"), dict)
                else None,
                "total_amount": float(order_dict.get("price", 0)),
                "currency": order_dict.get("currency", "RUB"),
                "created_at": created_at or datetime.utcnow(),
                "updated_at": updated_at or datetime.utcnow(),
                "items": items,
                "shipping_address": shipping_address,
                "fulfillment_type": "fbo",
                "raw_data": order_dict,
            }
        except Exception as e:
            logger.error(f"解析FBO订单数据失败: {str(e)}")
            return {
                "order_id": "",
                "order_number": "",
                "status": "",
                "customer_name": "",
                "customer_email": "",
                "total_amount": 0.0,
                "currency": "RUB",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "items": [],
                "shipping_address": {},
                "fulfillment_type": "fbo",
                "raw_data": {},
            }

    def _parse_fbs_order(self, order_data: Any) -> Dict[str, Any]:
        """解析Ozon FBS订单数据"""
        try:
            order_dict = (
                order_data.model_dump()
                if hasattr(order_data, "model_dump")
                else order_data
            )
            if not isinstance(order_dict, dict):
                order_dict = {}

            items = []
            products = order_dict.get("products", [])
            total_amount = 0.0
            for item in products:
                item_price = float(item.get("price", 0) or 0)
                item_quantity = item.get("quantity", 1)
                items.append(
                    {
                        "product_id": item.get("sku"),
                        "offer_id": item.get("offer_id"),
                        "name": item.get("name"),
                        "quantity": item_quantity,
                        "price": item_price,
                        "sku": item.get("sku"),
                    }
                )
                total_amount += item_price * item_quantity

            customer = order_dict.get("customer", {})
            customer_address = (
                customer.get("address", {}) if isinstance(customer, dict) else {}
            )

            shipping_address = {
                "city": customer_address.get("city", ""),
                "region": customer_address.get("region", ""),
                "address": customer_address.get("address_tail", ""),
                "postal_code": customer_address.get("zip_code", ""),
                "country": customer_address.get("country", ""),
                "recipient": customer.get("name", ""),
            }

            status = order_dict.get("status")
            status_str = (
                status.value
                if hasattr(status, "value")
                else str(status)
                if status
                else ""
            )

            created_at = self._parse_datetime(str(order_dict.get("in_process_at", "")))
            updated_at = datetime.utcnow()

            return {
                "order_id": str(order_dict.get("posting_number", "")),
                "order_number": order_dict.get(
                    "order_number", order_dict.get("posting_number", "")
                ),
                "status": status_str,
                "customer_name": customer.get("name", "")
                if isinstance(customer, dict)
                else "",
                "customer_email": None,
                "total_amount": total_amount,
                "currency": "CNY",
                "created_at": created_at or datetime.utcnow(),
                "updated_at": updated_at,
                "items": items,
                "shipping_address": shipping_address,
                "fulfillment_type": "fbs",
                "raw_data": order_dict,
            }
        except Exception as e:
            logger.error(f"解析FBS订单数据失败: {str(e)}")
            return {
                "order_id": "",
                "order_number": "",
                "status": "",
                "customer_name": "",
                "customer_email": "",
                "total_amount": 0.0,
                "currency": "RUB",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "items": [],
                "shipping_address": {},
                "fulfillment_type": "fbs",
                "raw_data": {},
            }

    async def get_all_products(self) -> List[Dict[str, Any]]:
        """获取所有Ozon商品（分页获取）"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.products.v3__product_list import (
                ProductListFilter,
                ProductListRequest,
            )

            all_products = []
            last_id = None
            page = 1
            max_pages = 50

            while page <= max_pages:
                filter_obj = ProductListFilter(visibility="ALL")
                request = ProductListRequest(
                    filter=filter_obj,
                    limit=100,
                    last_id=last_id,
                )

                response = await self._api.product_list(request)

                if (
                    not hasattr(response, "result")
                    or not response.result
                    or not hasattr(response.result, "items")
                    or not response.result.items
                ):
                    break

                for item in response.result.items:
                    item_dict = (
                        item.model_dump() if hasattr(item, "model_dump") else item
                    )
                    product_data = {
                        "product_id": item_dict.get("id")
                        or item_dict.get("product_id"),
                        "offer_id": item_dict.get("offer_id", ""),
                        "name": item_dict.get("name", ""),
                        "price": float(item_dict.get("price", 0) or 0),
                        "stock": item_dict.get("stock", 0) or 0,
                        "visibility": item_dict.get("visibility", "INVISIBLE"),
                        "category_id": item_dict.get("category_id"),
                        "created_at": self._parse_datetime(item_dict.get("created_at")),
                        "updated_at": self._parse_datetime(item_dict.get("updated_at")),
                    }
                    all_products.append(product_data)

                if (
                    not hasattr(response.result, "last_id")
                    or not response.result.last_id
                ):
                    break

                last_id = response.result.last_id
                page += 1
                await asyncio.sleep(0.5)

            logger.info(f"成功获取{len(all_products)}个Ozon商品（分{page - 1}页）")
            return all_products

        except APIError as e:
            logger.error(f"获取Ozon所有商品失败: {e}")
            raise OzonIntegrationError(f"获取所有商品失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon所有商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取所有商品错误: {str(e)}")

    async def sync_products_to_database(
        self, db, team_id: str, shop_id: str
    ) -> Dict[str, Any]:
        """同步Ozon商品到数据库"""
        self._ensure_connected()

        try:
            from app.models.database import OzonProduct

            all_products = await self.get_all_products()

            if not all_products:
                return {
                    "synced": 0,
                    "updated": 0,
                    "total": 0,
                    "message": "没有商品需要同步",
                }

            batch_size = 50
            all_product_details = []

            for i in range(0, len(all_products), batch_size):
                batch = all_products[i : i + batch_size]
                product_ids = [p["product_id"] for p in batch if p.get("product_id")]

                if product_ids:
                    try:
                        batch_details = await self.get_product_details(product_ids)

                        # Get product attributes for this batch
                        try:
                            product_attrs = await self.get_product_attributes_batch(
                                product_ids
                            )
                            # Merge attributes into details
                            for detail in batch_details:
                                pid = detail.get("id")
                                if pid in product_attrs:
                                    detail["product_attributes"] = product_attrs[pid]
                        except Exception as attr_err:
                            logger.warning(f"批量获取商品属性失败: {str(attr_err)}")

                        all_product_details.extend(batch_details)
                    except Exception as e:
                        logger.warning(
                            f"批量获取商品详情失败（批次{i // batch_size + 1}）: {str(e)}"
                        )
                        continue

                await asyncio.sleep(1)

            synced_count = 0
            updated_count = 0

            for detail in all_product_details:
                existing = await db.execute(
                    select(OzonProduct).where(
                        OzonProduct.team_id == team_id,
                        OzonProduct.shop_id == shop_id,
                        OzonProduct.ozon_product_id == detail.get("id"),
                    )
                )
                existing_product = existing.scalar_one_or_none()

                if existing_product:
                    exclude_fields = {"created_at", "id"}
                    for key, value in detail.items():
                        if key == "product_attributes":
                            key = "attributes"
                        if hasattr(existing_product, key) and key not in exclude_fields:
                            # Convert complex types to JSON strings for SQLite
                            if key == "primary_image" and isinstance(value, list):
                                value = value[0] if value else None
                            elif key == "images" and isinstance(value, list):
                                value = json.dumps(value) if value else "[]"
                            elif key == "barcodes" and isinstance(value, list):
                                value = json.dumps(value) if value else "[]"
                            elif key == "attributes" and isinstance(
                                value, (dict, list)
                            ):
                                value = json.dumps(value) if value else "{}"
                            elif key == "extra_data" and isinstance(
                                value, (dict, list)
                            ):
                                value = json.dumps(value) if value else "{}"
                            setattr(existing_product, key, value)

                    # Update category_name if category_id changed or not set
                    product_attrs = detail.get("product_attributes", {})
                    new_category_id = (
                        product_attrs.get("description_category_id")
                        if isinstance(product_attrs, dict)
                        else detail.get("description_category_id")
                    )
                    if new_category_id and (
                        not existing_product.category_name
                        or existing_product.category_id != new_category_id
                    ):
                        existing_product.category_name = (
                            await self.get_category_name_from_db(
                                db, team_id, new_category_id
                            )
                        )

                    existing_product.last_synced_at = datetime.utcnow()
                    existing_product.sync_status = "synced"
                    updated_count += 1
                else:
                    product_attrs = detail.get("product_attributes", {})
                    category_id = (
                        product_attrs.get("description_category_id")
                        if isinstance(product_attrs, dict)
                        else detail.get("description_category_id")
                    )

                    # Get category name from local database
                    category_name = None
                    if category_id:
                        category_name = await self.get_category_name_from_db(
                            db, team_id, category_id
                        )

                    new_product = OzonProduct(
                        team_id=team_id,
                        shop_id=shop_id,
                        ozon_product_id=detail.get("id"),
                        ozon_sku=detail.get("sources", [{}])[0].get("sku")
                        if isinstance(detail.get("sources"), list)
                        else None,
                        offer_id=detail.get("offer_id", ""),
                        title=detail.get("name", ""),
                        description=None,
                        brand=None,
                        category_id=category_id,
                        category_name=category_name,
                        type_id=product_attrs.get("type_id")
                        if isinstance(product_attrs, dict)
                        else detail.get("type_id"),
                        price=detail.get("price"),
                        old_price=detail.get("old_price"),
                        marketing_price=detail.get("marketing_price"),
                        currency=detail.get("currency_code", "RUB"),
                        stock=detail.get("stocks", {}).get("present", 0)
                        if isinstance(detail.get("stocks"), dict)
                        else 0,
                        reserved_stock=detail.get("stocks", {}).get("reserved", 0)
                        if isinstance(detail.get("stocks"), dict)
                        else 0,
                        stock_type=None,
                        status=detail.get("status", {}).get("status")
                        if isinstance(detail.get("status"), dict)
                        else None,
                        status_name=detail.get("status", {}).get("status_name")
                        if isinstance(detail.get("status"), dict)
                        else None,
                        moderate_status=None,
                        visibility="VISIBLE",
                        is_archived=detail.get("is_archived", False),
                        is_discounted=detail.get("is_discounted", False),
                        is_super=detail.get("is_super", False),
                        vat=detail.get("vat"),
                        commission_percent=None,
                        volume_weight=product_attrs.get("weight")
                        if isinstance(product_attrs, dict)
                        else detail.get("volume_weight"),
                        barcodes=json.dumps(product_attrs.get("barcodes", []))
                        if isinstance(product_attrs, dict)
                        else json.dumps(detail.get("barcodes", [])),
                        images=json.dumps(product_attrs.get("images", []))
                        if isinstance(product_attrs, dict)
                        else json.dumps(detail.get("images", [])),
                        primary_image=product_attrs.get("primary_image", [None])[0]
                        if isinstance(product_attrs.get("primary_image"), list)
                        else (
                            product_attrs.get("primary_image")
                            if isinstance(product_attrs, dict)
                            else None
                        ),
                        attributes=json.dumps(product_attrs)
                        if isinstance(product_attrs, dict)
                        else "{}",
                        last_synced_at=datetime.utcnow(),
                        sync_status="synced",
                    )
                    db.add(new_product)
                    synced_count += 1

            await db.commit()

            logger.info(
                f"Ozon商品同步完成: 新增{synced_count}个, 更新{updated_count}个"
            )
            return {
                "synced": synced_count,
                "updated": updated_count,
                "total": len(all_product_details),
                "message": f"同步完成: 新增{synced_count}个, 更新{updated_count}个",
            }

        except Exception as e:
            logger.error(f"同步Ozon商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"同步商品错误: {str(e)}")

    async def get_category_name_from_db(
        self, db, team_id: str, description_category_id: int
    ) -> Optional[str]:
        """从本地数据库获取分类名称"""
        try:
            from app.models.database import OzonCategoryTree

            result = await db.execute(
                select(OzonCategoryTree).where(
                    and_(
                        OzonCategoryTree.team_id == team_id,
                        OzonCategoryTree.description_category_id
                        == description_category_id,
                    )
                )
            )
            category = result.scalar_one_or_none()
            if category:
                return category.category_name
            return None
        except Exception as e:
            logger.warning(f"获取分类名称失败: {str(e)}")
            return None

    async def sync_orders_to_database(
        self, db, team_id: str, shop_id: str, days_back: int = 7
    ) -> Dict[str, Any]:
        """同步Ozon订单到数据库"""
        self._ensure_connected()

        try:
            from datetime import timedelta

            from app.models.database import (
                Customer,
                Order,
                OrderItem,
                OrderStatusHistory,
                PlatformProduct,
            )

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            orders = await self.get_orders(start_date=start_date, end_date=end_date)

            if not orders:
                return {
                    "synced": 0,
                    "updated": 0,
                    "total": 0,
                    "message": f"没有找到{days_back}天内的Ozon订单",
                }

            synced_count = 0
            updated_count = 0

            for ozon_order in orders:
                existing = await db.execute(
                    select(Order).where(
                        Order.team_id == team_id,
                        Order.shop_id == shop_id,
                        Order.platform_order_id == ozon_order.order_id,
                    )
                )
                existing_order = existing.scalar_one_or_none()

                if existing_order:
                    existing_order.order_number = ozon_order.order_number
                    existing_order.status = ozon_order.status
                    existing_order.customer_name = ozon_order.customer_name or ""
                    existing_order.customer_email = ozon_order.customer_email or ""
                    existing_order.total_amount = float(ozon_order.total_amount)
                    existing_order.currency = ozon_order.currency
                    existing_order.updated_at = datetime.utcnow()

                    fulfillment_type = (
                        ozon_order.raw_data.get("fulfillment_type", "unknown")
                        if isinstance(ozon_order.raw_data, dict)
                        else "unknown"
                    )
                    if not existing_order.extra_data:
                        existing_order.extra_data = {}
                    existing_order.extra_data["fulfillment_type"] = fulfillment_type

                    if existing_order.status != ozon_order.status:
                        status_history = OrderStatusHistory(
                            order_id=existing_order.id,
                            status=ozon_order.status,
                            notes="从Ozon同步，状态更新",
                        )
                        db.add(status_history)

                    updated_count += 1
                else:
                    customer = None
                    if ozon_order.customer_email:
                        customer_result = await db.execute(
                            select(Customer).where(
                                Customer.team_id == team_id,
                                Customer.email == ozon_order.customer_email,
                            )
                        )
                        customer = customer_result.scalar_one_or_none()

                    if not customer and (
                        ozon_order.customer_email or ozon_order.customer_name
                    ):
                        customer = Customer(
                            team_id=team_id,
                            name=ozon_order.customer_name or "",
                            email=ozon_order.customer_email or "",
                            phone="",
                            first_order_date=datetime.utcnow(),
                            last_order_date=datetime.utcnow(),
                            total_orders=1,
                            total_spent=float(ozon_order.total_amount),
                        )
                        db.add(customer)
                        await db.flush()

                    fulfillment_type = (
                        ozon_order.raw_data.get("fulfillment_type", "unknown")
                        if isinstance(ozon_order.raw_data, dict)
                        else "unknown"
                    )

                    shipping_address_dict = (
                        ozon_order.shipping_address
                        if isinstance(ozon_order.shipping_address, dict)
                        else {}
                    )

                    new_order = Order(
                        team_id=team_id,
                        shop_id=shop_id,
                        platform_order_id=ozon_order.order_id,
                        order_number=ozon_order.order_number,
                        customer_id=customer.id if customer else None,
                        customer_name=ozon_order.customer_name or "",
                        customer_email=ozon_order.customer_email or "",
                        customer_phone="",
                        shipping_address=shipping_address_dict,
                        currency=ozon_order.currency,
                        subtotal_amount=float(ozon_order.total_amount),
                        shipping_amount=0.0,
                        tax_amount=0.0,
                        discount_amount=0.0,
                        total_amount=float(ozon_order.total_amount),
                        payment_status="pending",
                        fulfillment_status="unfulfilled",
                        status=ozon_order.status,
                        notes=f"从Ozon同步",
                        extra_data={"fulfillment_type": fulfillment_type},
                    )
                    db.add(new_order)
                    await db.flush()

                    for item in ozon_order.items:
                        item_price = float(item.get("price", 0))
                        item_quantity = item.get("quantity", 1)
                        item_total = item_price * item_quantity
                        item_sku = item.get("sku", "")

                        product_id = None
                        if item_sku:
                            platform_product_result = await db.execute(
                                select(PlatformProduct).where(
                                    PlatformProduct.shop_id == shop_id,
                                    PlatformProduct.platform_sku == str(item_sku),
                                )
                            )
                            platform_product = (
                                platform_product_result.scalar_one_or_none()
                            )
                            if platform_product:
                                product_id = platform_product.product_id

                        order_item = OrderItem(
                            order_id=new_order.id,
                            product_id=product_id,
                            sku=item.get("sku", ""),
                            title=item.get("name", ""),
                            quantity=item_quantity,
                            unit_price=item_price,
                            subtotal=item_total,
                            total_amount=item_total,
                        )
                        db.add(order_item)

                    status_history = OrderStatusHistory(
                        order_id=new_order.id,
                        status=ozon_order.status,
                        notes="从Ozon同步的初始状态",
                    )
                    db.add(status_history)

                    synced_count += 1

            await db.commit()

            logger.info(
                f"Ozon订单同步完成: 新增{synced_count}个, 更新{updated_count}个"
            )
            return {
                "synced": synced_count,
                "updated": updated_count,
                "total": len(orders),
                "message": f"同步完成: 新增{synced_count}个, 更新{updated_count}个",
            }

        except Exception as e:
            logger.error(f"同步Ozon订单时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"同步订单错误: {str(e)}")

    async def get_warehouses(self) -> List[OzonWarehouse]:
        """获取Ozon仓库列表"""
        self._ensure_connected()

        try:
            result = await self._api.warehouse_list()

            warehouses = []
            if hasattr(result, "result") and result.result:
                for warehouse_data in result.result:
                    wh_dict = (
                        warehouse_data
                        if isinstance(warehouse_data, dict)
                        else warehouse_data.model_dump()
                        if hasattr(warehouse_data, "model_dump")
                        else {}
                    )
                    warehouse = OzonWarehouse(
                        warehouse_id=str(wh_dict.get("warehouse_id", "")),
                        name=wh_dict.get("name", ""),
                        is_fbos=wh_dict.get("is_fbos", False),
                        is_fbs=wh_dict.get("is_fbs", False),
                        is_premium=wh_dict.get("is_premium", False),
                        type=wh_dict.get("type"),
                        address=wh_dict.get("address"),
                        raw_data=wh_dict,
                    )
                    warehouses.append(warehouse)

            logger.info(f"成功获取{len(warehouses)}个Ozon仓库")
            return warehouses

        except APIError as e:
            logger.error(f"获取Ozon仓库失败: {e}")
            raise OzonIntegrationError(f"获取仓库失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon仓库时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取仓库错误: {str(e)}")

    async def get_delivery_methods(self) -> List[OzonDeliveryMethod]:
        """获取Ozon配送方式列表"""
        self._ensure_connected()

        try:
            result = await self._api.delivery_method_list()

            methods = []
            if hasattr(result, "result") and result.result:
                for method_data in result.result:
                    md_dict = (
                        method_data
                        if isinstance(method_data, dict)
                        else method_data.model_dump()
                        if hasattr(method_data, "model_dump")
                        else {}
                    )
                    method = OzonDeliveryMethod(
                        delivery_method_id=md_dict.get("delivery_method_id", ""),
                        name=md_dict.get("name", ""),
                        warehouse_id=str(md_dict.get("warehouse_id", "")),
                        warehouse_name=md_dict.get("warehouse_name"),
                        price=md_dict.get("price", 0),
                        raw_data=md_dict,
                    )
                    methods.append(method)

            logger.info(f"成功获取{len(methods)}个Ozon配送方式")
            return methods

        except APIError as e:
            logger.error(f"获取Ozon配送方式失败: {e}")
            raise OzonIntegrationError(f"获取配送方式失败: {e}")
        except Exception as e:
            logger.error(f"获取Ozon配送方式时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取配送方式错误: {str(e)}")

    async def get_product_prices(
        self, product_ids: Optional[List[int]] = None
    ) -> List[OzonProductPrice]:
        """获取商品价格信息"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.prices_and_stocks.v5__product_info_prices import (
                ProductInfoPricesFilter,
                ProductInfoPricesRequest,
            )

            filter_obj = ProductInfoPricesFilter(
                product_id=product_ids if product_ids else [],
            )

            request = ProductInfoPricesRequest(
                filter=filter_obj,
                limit=100,
            )

            result = await self._api.product_info_prices(request)

            prices = []
            if hasattr(result, "result") and result.result:
                for price_data in result.result.items:
                    pd = (
                        price_data
                        if isinstance(price_data, dict)
                        else price_data.model_dump()
                        if hasattr(price_data, "model_dump")
                        else {}
                    )
                    price = OzonProductPrice(
                        product_id=pd.get("product_id", 0),
                        offer_id=pd.get("offer_id", ""),
                        price=pd.get("price", 0),
                        old_price=pd.get("old_price"),
                        marketing_price=pd.get("marketing_price"),
                        currency=pd.get("currency", "RUB"),
                        raw_data=pd,
                    )
                    prices.append(price)

            logger.info(f"成功获取{len(prices)}个商品价格信息")
            return prices

        except APIError as e:
            logger.error(f"获取商品价格失败: {e}")
            raise OzonIntegrationError(f"获取价格失败: {e}")
        except Exception as e:
            logger.error(f"获取商品价格时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取价格错误: {str(e)}")

    async def get_product_stocks(
        self, product_ids: Optional[List[int]] = None
    ) -> List[OzonProductStock]:
        """获取商品库存信息"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas.prices_and_stocks.v4__product_info_stocks import (
                ProductInfoStocksFilter,
                ProductInfoStocksRequest,
            )

            filter_obj = ProductInfoStocksFilter(
                product_id=product_ids if product_ids else [],
            )

            request = ProductInfoStocksRequest(
                filter=filter_obj,
                limit=100,
            )

            result = await self._api.product_info_stocks(request)

            stocks = []
            if hasattr(result, "result") and result.result:
                for stock_data in result.result.items:
                    sd = (
                        stock_data
                        if isinstance(stock_data, dict)
                        else stock_data.model_dump()
                        if hasattr(stock_data, "model_dump")
                        else {}
                    )
                    stock = OzonProductStock(
                        product_id=sd.get("product_id", 0),
                        offer_id=sd.get("offer_id", ""),
                        stock=sd.get("stock", 0),
                        reserved_stock=sd.get("reserved_stock", 0),
                        warehouse_id=sd.get("warehouse_id"),
                        stock_type=sd.get("type"),
                        raw_data=sd,
                    )
                    stocks.append(stock)

            logger.info(f"成功获取{len(stocks)}个商品库存信息")
            return stocks

        except APIError as e:
            logger.error(f"获取商品库存失败: {e}")
            raise OzonIntegrationError(f"获取库存失败: {e}")
        except Exception as e:
            logger.error(f"获取商品库存时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取库存错误: {str(e)}")

    async def update_product_prices(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量更新商品价格"""
        self._ensure_connected()

        try:
            result = await self._api.product_import_prices(items=items)

            logger.info(f"成功更新商品价格")
            return result.model_dump() if hasattr(result, "model_dump") else {}

        except APIError as e:
            logger.error(f"更新商品价格失败: {e}")
            raise OzonIntegrationError(f"更新价格失败: {e}")
        except Exception as e:
            logger.error(f"更新商品价格时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"更新价格错误: {str(e)}")

    async def update_product_stocks(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量更新商品库存"""
        self._ensure_connected()

        try:
            result = await self._api.products_stocks(items=items)

            logger.info(f"成功更新商品库存")
            return result.model_dump() if hasattr(result, "model_dump") else {}

        except APIError as e:
            logger.error(f"更新商品库存失败: {e}")
            raise OzonIntegrationError(f"更新库存失败: {e}")
        except Exception as e:
            logger.error(f"更新商品库存时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"更新库存错误: {str(e)}")

    async def get_seller_info(self) -> OzonSellerInfo:
        """获取卖家信息"""
        self._ensure_connected()

        try:
            result = await self._api.seller_info()

            seller_data = {}
            if hasattr(result, "result") and result.result:
                seller_data = result.result if isinstance(result.result, dict) else {}

            seller_info = OzonSellerInfo(
                seller_id=seller_data.get("id", 0),
                name=seller_data.get("name", ""),
                company=seller_data.get("company", ""),
                manager_id=seller_data.get("manager_id"),
                raw_data=seller_data,
            )

            logger.info(f"成功获取卖家信息: {seller_info.name}")
            return seller_info

        except APIError as e:
            logger.error(f"获取卖家信息失败: {e}")
            raise OzonIntegrationError(f"获取卖家信息失败: {e}")
        except Exception as e:
            logger.error(f"获取卖家信息时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取卖家信息错误: {str(e)}")

    async def get_product_description(
        self, product_id: int
    ) -> Optional[Dict[str, Any]]:
        """获取商品描述"""
        self._ensure_connected()

        try:
            result = await self._api.product_info_description(product_id=[product_id])

            if hasattr(result, "result") and result.result:
                if str(product_id) in result.result:
                    return result.result[str(product_id)]
            return None

        except APIError as e:
            logger.error(f"获取商品描述失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取商品描述时发生未知错误: {str(e)}")
            return None

    async def get_product_attributes(
        self, product_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """获取商品属性"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import (
                ProductInfoAttributesRequest,
                ProductInfoAttributesFilter,
            )

            request = ProductInfoAttributesRequest(
                filter=ProductInfoAttributesFilter(
                    product_id=[product_id],
                ),
                limit=100,
            )
            result = await self._api.product_info_attributes(request=request)

            if hasattr(result, "result") and result.result:
                attributes = []
                for item in result.result:
                    if hasattr(item, "model_dump"):
                        attributes.append(item.model_dump())
                    else:
                        attributes.append(dict(item))
                return attributes
            return None

        except APIError as e:
            logger.error(f"获取商品属性失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取商品属性时发生未知错误: {str(e)}")
            return None

    async def get_product_attributes_batch(
        self, product_ids: List[int]
    ) -> Dict[int, List[Dict[str, Any]]]:
        """批量获取商品属性"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import (
                ProductInfoAttributesRequest,
                ProductInfoAttributesFilter,
            )

            request = ProductInfoAttributesRequest(
                filter=ProductInfoAttributesFilter(
                    product_id=product_ids,
                ),
                limit=1000,
            )
            result = await self._api.product_info_attributes(request=request)

            attributes_map = {}
            if hasattr(result, "result") and result.result:
                for item in result.result:
                    # Find the product_id for this item
                    item_dict = (
                        item.model_dump() if hasattr(item, "model_dump") else dict(item)
                    )
                    pid = None
                    for pid_check in product_ids:
                        # Each item should have attributes, find by presence
                        pass

                    # The API returns list, map by index
                    if hasattr(result, "result"):
                        for idx, ritem in enumerate(result.result):
                            if idx < len(product_ids):
                                pid = product_ids[idx]
                                attr_dict = (
                                    ritem.model_dump()
                                    if hasattr(ritem, "model_dump")
                                    else dict(ritem)
                                )
                                attributes_map[pid] = attr_dict

            return attributes_map

        except APIError as e:
            logger.error(f"批量获取商品属性失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"批量获取商品属性时发生未知错误: {str(e)}")
            return {}

    async def get_fbo_order_detail(self, posting_number: str) -> Dict[str, Any]:
        """获取FBO订单详情"""
        self._ensure_connected()

        try:
            result = await self._api.posting_fbo_get(posting_number=posting_number)

            logger.info(f"成功获取FBO订单详情: {posting_number}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"获取FBO订单详情失败: {e}")
            raise OzonIntegrationError(f"获取订单详情失败: {e}")
        except Exception as e:
            logger.error(f"获取FBO订单详情时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取订单详情错误: {str(e)}")

    async def get_fbs_order_detail(self, posting_number: str) -> Dict[str, Any]:
        """获取FBS订单详情"""
        self._ensure_connected()

        try:
            result = await self._api.posting_fbs_get(posting_number=posting_number)

            logger.info(f"成功获取FBS订单详情: {posting_number}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"获取FBS订单详情失败: {e}")
            raise OzonIntegrationError(f"获取订单详情失败: {e}")
        except Exception as e:
            logger.error(f"获取FBS订单详情时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取订单详情错误: {str(e)}")

    async def cancel_fbs_order(
        self, posting_number: str, cancel_reason: str
    ) -> Dict[str, Any]:
        """取消FBS订单"""
        self._ensure_connected()

        try:
            result = await self._api.posting_fbs_cancel(
                posting_number=posting_number, cancel_reason=cancel_reason
            )

            logger.info(f"成功取消FBS订单: {posting_number}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"取消FBS订单失败: {e}")
            raise OzonIntegrationError(f"取消订单失败: {e}")
        except Exception as e:
            logger.error(f"取消FBS订单时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"取消订单错误: {str(e)}")

    async def get_product_rating(self, sku: str) -> Optional[Dict[str, Any]]:
        """获取商品评分"""
        self._ensure_connected()

        try:
            result = await self._api.product_rating_by_sku(sku=sku)

            logger.info(f"成功获取商品评分: {sku}")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"获取商品评分失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取商品评分时发生未知错误: {str(e)}")
            return None

    async def get_category_attributes(
        self, category_id: int, type_id: int
    ) -> List[Dict[str, Any]]:
        """获取分类属性"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import DescriptionCategoryAttributeRequest

            request = DescriptionCategoryAttributeRequest(
                description_category_id=category_id,
                type_id=type_id,
            )
            result = await self._api.description_category_attribute(request=request)

            attributes = []
            if hasattr(result, "result") and result.result:
                attributes = result.result

            logger.info(f"成功获取分类{category_id}的{len(attributes)}个属性")
            return attributes

        except APIError as e:
            logger.error(f"获取分类属性失败: {e}")
            raise OzonIntegrationError(f"获取分类属性失败: {e}")
        except Exception as e:
            logger.error(f"获取分类属性时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取分类属性错误: {str(e)}")

    async def import_product_images(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """导入商品图片"""
        self._ensure_connected()

        try:
            payload = {"items": items}

            result = await self._api._request(
                method="post",
                api_version="v1",
                endpoint="product/import/pictures",
                json=payload,
            )

            logger.info(f"成功导入商品图片")
            return result.get("result", {})

        except APIError as e:
            logger.error(f"导入商品图片失败: {e}")
            raise OzonIntegrationError(f"导入图片失败: {e}")
        except Exception as e:
            logger.error(f"导入商品图片时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"导入图片错误: {str(e)}")

    async def delete_products(self, product_ids: List[int]) -> Dict[str, Any]:
        """删除商品"""
        self._ensure_connected()

        try:
            result = await self._api.products_delete(product_id=product_ids)

            logger.info(f"成功删除{len(product_ids)}个商品")
            return result.model_dump() if hasattr(result, "model_dump") else result

        except APIError as e:
            logger.error(f"删除商品失败: {e}")
            raise OzonIntegrationError(f"删除商品失败: {e}")
        except Exception as e:
            logger.error(f"删除商品时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"删除商品错误: {str(e)}")

    async def get_analytics_stocks(
        self, warehouse_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取库存分析数据"""
        self._ensure_connected()

        try:
            payload = {}
            if warehouse_id:
                payload["warehouse_id"] = warehouse_id

            result = await self._api._request(
                method="post",
                api_version="v1",
                endpoint="analytics/stocks",
                json=payload,
            )

            stocks = result.get("result", [])
            logger.info(f"成功获取{len(stocks)}条库存分析数据")
            return stocks

        except APIError as e:
            logger.error(f"获取库存分析数据失败: {e}")
            raise OzonIntegrationError(f"获取库存分析失败: {e}")
        except Exception as e:
            logger.error(f"获取库存分析数据时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取库存分析错误: {str(e)}")

    async def get_unfulfilled_postings(self) -> List[Dict[str, Any]]:
        """获取未完成的发货请求列表"""
        self._ensure_connected()

        try:
            result = await self._api.posting_fbs_unfulfilled_list(limit=100)

            postings = []
            if hasattr(result, "result") and result.result:
                postings = result.result

            logger.info(f"成功获取{len(postings)}个未完成的发货请求")
            return postings

        except APIError as e:
            logger.error(f"获取未完成发货请求失败: {e}")
            raise OzonIntegrationError(f"获取未完成发货请求失败: {e}")
        except Exception as e:
            logger.error(f"获取未完成发货请求时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取未完成发货请求错误: {str(e)}")

    async def get_description_category_tree(
        self, language: str = "ZH_HANS"
    ) -> List[Dict[str, Any]]:
        """获取商品分类树"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import DescriptionCategoryTreeRequest

            request = DescriptionCategoryTreeRequest(language=language)
            result = await self._api.description_category_tree(request=request)

            categories = []
            if hasattr(result, "result") and result.result:
                for item in result.result:
                    if hasattr(item, "model_dump"):
                        categories.append(item.model_dump())
                    else:
                        categories.append(dict(item))

            logger.info(f"成功获取{len(categories)}个分类")
            return categories

        except APIError as e:
            logger.error(f"获取分类树失败: {e}")
            raise OzonIntegrationError(f"获取分类树失败: {e}")
        except Exception as e:
            logger.error(f"获取分类树时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取分类树错误: {str(e)}")

    async def get_category_attributes(
        self,
        description_category_id: int,
        type_id: int,
        language: str = "ZH_HANS",
    ) -> List[Dict[str, Any]]:
        """获取指定分类和类型的属性"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import (
                DescriptionCategoryAttributeRequest,
            )

            request = DescriptionCategoryAttributeRequest(
                description_category_id=description_category_id,
                type_id=type_id,
                language=language,
            )
            result = await self._api.description_category_attribute(request=request)

            attributes = []
            if hasattr(result, "result") and result.result:
                for item in result.result:
                    if hasattr(item, "model_dump"):
                        attributes.append(item.model_dump())
                    else:
                        attributes.append(dict(item))

            logger.info(f"成功获取{len(attributes)}个属性")
            return attributes

        except APIError as e:
            logger.error(f"获取分类属性失败: {e}")
            raise OzonIntegrationError(f"获取分类属性失败: {e}")
        except Exception as e:
            logger.error(f"获取分类属性时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取分类属性错误: {str(e)}")

    async def get_description_category_attribute(
        self,
        description_category_id: int,
        type_id: int,
        language: str = "ZH_HANS",
    ) -> List[Dict[str, Any]]:
        """获取指定分类和类型的属性（描述分类API）"""
        return await self.get_category_attributes(
            description_category_id=description_category_id,
            type_id=type_id,
            language=language,
        )

    async def get_attribute_values(
        self,
        description_category_id: int,
        type_id: int,
        attribute_id: int,
        limit: int = 2000,
        language: str = "ZH_HANS",
        last_value_id: int = 0,
    ) -> List[Dict[str, Any]]:
        """获取属性的可选值列表"""
        self._ensure_connected()

        try:
            from ozonapi.seller.schemas import (
                DescriptionCategoryAttributeValuesRequest,
            )

            request = DescriptionCategoryAttributeValuesRequest(
                description_category_id=description_category_id,
                type_id=type_id,
                attribute_id=attribute_id,
                limit=limit,
                language=language,
                last_value_id=last_value_id if last_value_id > 0 else None,
            )
            result = await self._api.description_category_attribute_values(
                request=request
            )

            values = []
            if hasattr(result, "result") and result.result:
                for item in result.result:
                    if hasattr(item, "model_dump"):
                        values.append(item.model_dump())
                    else:
                        values.append(dict(item))

            logger.info(f"成功获取{len(values)}个属性值")
            return values

        except APIError as e:
            logger.error(f"获取属性值失败: {e}")
            raise OzonIntegrationError(f"获取属性值失败: {e}")
        except Exception as e:
            logger.error(f"获取属性值时发生未知错误: {str(e)}")
            raise OzonIntegrationError(f"获取属性值错误: {str(e)}")
