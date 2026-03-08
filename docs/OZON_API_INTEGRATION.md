# Ozon API 集成指南

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v1.0 |
| **最后更新** | 2026-02-18 |
| **适用对象** | 开发工程师、集成工程师 |
| **技术栈** | Python 3.10+, AsyncIO, aiohttp, Pydantic |
| **相关文档** | [API设计文档](API_DESIGN.md), [开发指南](DEVELOPMENT_GUIDE.md) |

## 1. Ozon API 库概述

### 1.1 项目位置
项目位于 `D:\iCross\python-ozon-api-main`，是一个完整的Python Ozon Seller API客户端库。

### 1.2 核心特性
- ✨ **完全异步**：基于AsyncIO和aiohttp实现
- 🛡️ **强类型支持**：使用Pydantic进行数据验证和类型提示
- 🚀 **高性能**：内置请求限流和重试机制
- 📦 **功能全面**：覆盖Ozon Seller API主要功能模块
- 🔧 **易于扩展**：模块化设计，易于添加新API方法

### 1.3 技术架构
```
python-ozon-api-main/
├── ozon_api/                    # 核心库
│   ├── __init__.py             # 主入口点，导出OzonAPI类
│   ├── base.py                 # 基础客户端类 (OzonAPIBase)
│   ├── exceptions.py           # 异常类定义
│   ├── methods/                # API方法实现
│   │   ├── category.py         # 分类相关API
│   │   ├── product_list.py     # 商品列表API
│   │   ├── product_import.py   # 商品导入API
│   │   ├── product_archive.py  # 商品归档API
│   │   └── ...                 # 其他API方法
│   └── models/                 # 数据模型
│       ├── product_list.py     # 商品列表模型
│       ├── product_import.py   # 商品导入模型
│       └── ...                 # 其他数据模型
├── tests/                      # 测试文件
├── pyproject.toml             # 项目配置
├── README.md                  # 项目说明
└── implemented_methods_list.md # 已实现方法列表
```

## 2. 安装与配置

### 2.1 安装方式

#### 方式一：作为Python包安装
```bash
# 从本地目录安装
pip install -e D:\iCross\python-ozon-api-main

# 或使用uv（推荐）
uv pip install -e D:\iCross\python-ozon-api-main
```

#### 方式二：作为子模块集成
```bash
# 将目录复制到项目中
cp -r python-ozon-api-main/ozon_api backend/app/integrations/ozon_api
```

#### 方式三：直接导入使用
```python
import sys
sys.path.append('D:\iCross\python-ozon-api-main')
from ozon_api import OzonAPI
```

### 2.2 环境配置

在 `.env` 文件中配置Ozon API凭证：
```env
# Ozon API配置
OZON_CLIENT_ID=your-client-id
OZON_API_KEY=your-api-key
OZON_API_URL=https://api-seller.ozon.ru
```

### 2.3 依赖项

主要依赖：
- `aiohttp >= 3.9.0` - 异步HTTP客户端
- `pydantic >= 2.5.0` - 数据验证和序列化
- `tenacity >= 8.2.0` - 重试机制
- `loguru >= 0.7.0` - 结构化日志记录

## 3. 已实现的API方法

### 3.1 商品管理

| 方法 | API端点 | 功能描述 | 支持版本 |
|------|---------|----------|----------|
| `product_list` | POST `/v3/product/list` | 获取商品列表 | v3 |
| `product_info_limit` | POST `/v4/product/info/limit` | 获取商品限制信息 | v4 |
| `product_info_attributes` | POST `/v3/product/info/attributes` | 获取商品属性描述 | v3 |
| `product_info_list` | POST `/v3/product/info/list` | 根据ID获取商品信息 | v3 |
| `product_import` | POST `/v3/product/import` | 导入商品 | v3 |
| `product_import_info` | POST `/v1/product/import/info` | 获取导入任务状态 | v1 |
| `product_import_by_sku` | POST `/v1/product/import-by-sku` | 根据SKU导入商品 | v1 |
| `product_attributes_update` | POST `/v1/product/attributes/update` | 更新商品属性 | v1 |
| `products_delete` | POST `/v2/products/delete` | 删除商品 | v2 |
| `product_update_offer_id` | POST `/v1/product/update/offer-id` | 更新offer_id | v1 |
| `product_archive` | POST `/v1/product/archive` | 商品归档 | v1 |
| `product_unarchive` | POST `/v1/product/unarchive` | 商品取消归档 | v1 |

### 3.2 分类管理

| 方法 | API端点 | 功能描述 | 支持版本 |
|------|---------|----------|----------|
| `get_description_category_tree` | POST `/v1/description-category/tree` | 获取分类树 | v1 |
| `get_description_category_attribute` | POST `/v1/description-category/attribute` | 获取分类属性 | v1 |
| `get_description_category_attribute_values` | POST `/v1/description-category/attribute/values` | 获取分类属性值 | v1 |
| `get_description_category_attribute_values_search` | POST `/v1/description-category/attribute/values/search` | 搜索分类属性值 | v1 |
| `get_full_category_info` | 组合方法 | 获取完整分类信息 | 自定义 |

### 3.3 图片管理

| 方法 | API端点 | 功能描述 | 支持版本 |
|------|---------|----------|----------|
| `product_pictures_import` | POST `/v1/product/pictures/import` | 导入商品图片 | v1 |
| `product_pictures_info` | POST `/v2/product/pictures/info` | 获取图片信息 | v2 |

### 3.4 条码管理

| 方法 | API端点 | 功能描述 | 支持版本 |
|------|---------|----------|----------|
| `product_barcode_add` | POST `/v1/barcode/add` | 添加商品条码 | v1 |
| `product_barcode_generate` | POST `/v1/barcode/generate` | 生成商品条码 | v1 |

### 3.5 其他功能

| 方法 | API端点 | 功能描述 | 支持版本 |
|------|---------|----------|----------|
| `upload_digital_codes` | POST `/v1/product/upload_digital_codes` | 上传数字代码 | v1 |
| `upload_digital_codes_info` | POST `/v1/product/upload_digital_codes/info` | 获取上传状态 | v1 |
| `product_subscription` | POST `/v1/product/info/subscription` | 商品信息订阅 | v1 |
| `product_related_sku` | POST `/v1/product/related-sku/get` | 获取相关SKU | v1 |
| `product_rating_by_sku` | POST `/v1/product/rating-by-sku` | 获取商品评分 | v1 |

## 4. 基础使用示例

### 4.1 初始化客户端

```python
import asyncio
from ozon_api import OzonAPI

async def main():
    # 推荐方式：使用上下文管理器
    async with OzonAPI(
        client_id="your-client-id",
        api_key="your-api-key"
    ) as api:
        # API调用...
        pass
    
    # 替代方式：手动管理
    api = OzonAPI(client_id="your-client-id", api_key="your-api-key")
    try:
        # API调用...
        pass
    finally:
        # 需要手动关闭会话
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 配置选项

```python
# 设置API端点（如果需要自定义）
api.api_url = "https://api-seller.ozon.ru"

# 设置语言（支持: DEFAULT, RU, EN, TR, ZH_HANS）
api.language = "RU"

# 设置描述分类ID
api.description_category_id = 12345

# 设置商品类型ID
api.type_id = 1
```

### 4.3 错误处理

```python
from ozon_api.exceptions import (
    OzonAPIClientError,
    OzonAPIForbiddenError,
    OzonAPINotFoundError,
    OzonAPIConflictError,
    OzonAPIServerError,
    OzonAPIError,
)

async def safe_api_call():
    try:
        response = await api.product_list(request)
        return response
    except OzonAPIClientError as e:
        print(f"客户端错误: {e.message} (代码: {e.code})")
        # 处理客户端错误（如验证失败、参数错误）
    except OzonAPIForbiddenError as e:
        print(f"权限错误: {e.message}")
        # 处理权限不足
    except OzonAPINotFoundError as e:
        print(f"资源未找到: {e.message}")
        # 处理资源不存在
    except OzonAPIConflictError as e:
        print(f"数据冲突: {e.message}")
        # 处理数据冲突
    except OzonAPIServerError as e:
        print(f"服务器错误: {e.message}")
        # 重试或降级处理
    except OzonAPIError as e:
        print(f"API错误: {e.message}")
        # 通用错误处理
```

## 5. 核心功能示例

### 5.1 获取商品列表

```python
from ozon_api.models.product_list import ProductListRequest, ProductListFilter

async def get_product_list():
    # 创建请求参数
    filter_obj = ProductListFilter(
        offer_id=["ART001", "ART002"],
        visibility="VISIBLE"
    )
    
    request = ProductListRequest(
        filter=filter_obj,
        limit=100,
        last_id=None,
        sort_by="product_id",
        sort_dir="ASC"
    )
    
    # 调用API
    response = await api.product_list(request)
    
    # 处理响应
    for item in response.result.items:
        print(f"商品ID: {item['product_id']}, 货号: {item['offer_id']}")
    
    return response
```

### 5.2 导入商品

```python
from ozon_api.models.product_import import ProductImport, ProductImportItem

async def import_products():
    # 创建商品数据
    items = [
        ProductImportItem(
            attributes=[
                {"attribute_id": 85, "values": [{"value": "笔记本电脑"}]},
                {"attribute_id": 8229, "values": [{"value": "Apple"}]},
                {"attribute_id": 9028, "values": [{"value": "MacBook Air"}]},
            ],
            barcode="123456789012",
            description="高性能笔记本电脑",
            dimension_unit="mm",
            height=10,
            images=[
                {"file_name": "image1.jpg", "default": True},
                {"file_name": "image2.jpg", "default": False},
            ],
            name="MacBook Air 13英寸",
            offer_id="MBK001",
            price="99900",
            vat="0",
            weight=1300,
            weight_unit="g",
            width=300,
            depth=210,
        )
    ]
    
    request = ProductImport(items=items)
    
    # 导入商品
    result = await api.product_import(request)
    
    print(f"导入任务ID: {result.get('task_id')}")
    return result
```

### 5.3 获取分类信息

```python
async def get_category_tree():
    # 获取分类树
    tree_response = await api.get_description_category_tree()
    
    # 获取分类属性
    api.description_category_id = 17031234  # 设置目标分类ID
    attributes = await api.get_description_category_attribute()
    
    # 获取完整分类信息
    full_info = await api.get_full_category_info()
    
    return {
        "tree": tree_response,
        "attributes": attributes,
        "full_info": full_info
    }
```

### 5.4 商品图片管理

```python
from ozon_api.models.product_pictures import ProductPicturesRequest, ProductPicture

async def upload_product_images(product_id: str):
    # 准备图片数据
    images = [
        ProductPicture(
            file_name="main_image.jpg",
            default=True,
            index=0
        ),
        ProductPicture(
            file_name="detail_image.jpg",
            default=False,
            index=1
        )
    ]
    
    request = ProductPicturesRequest(
        product_id=product_id,
        images=images
    )
    
    # 上传图片
    result = await api.product_pictures_import(request)
    
    # 获取上传状态
    info_result = await api.product_pictures_info(request)
    
    return {
        "upload_result": result,
        "info": info_result
    }
```

### 5.5 批量操作

```python
async def batch_operations():
    # 批量获取商品信息
    product_ids = [12345, 12346, 12347]
    
    # 创建任务列表
    tasks = []
    for product_id in product_ids:
        # 注意：实际API可能需要不同的请求方式
        # 这里仅为示例
        tasks.append(get_product_info(product_id))
    
    # 并发执行
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    successful = []
    failed = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append((product_ids[i], str(result)))
        else:
            successful.append((product_ids[i], result))
    
    return {
        "successful": successful,
        "failed": failed,
        "total": len(product_ids)
    }
```

## 6. 与iCross系统集成方案

### 6.1 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  iCross业务层    │    │  Ozon适配层     │    │  Ozon API客户端  │
│  ProductService │────│  OzonAdapter    │────│  OzonAPI        │
│  OrderService   │    │  · 数据转换      │    │  · 原生API调用   │
│  InventoryService│    │  · 错误处理      │    │  · 限流重试      │
└─────────────────┘    │  · 日志记录      │    └─────────────────┘
                       └─────────────────┘
```

### 6.2 集成适配层设计

在 `backend/app/integrations/ozon/` 目录下创建适配层：

```
backend/app/integrations/ozon/
├── __init__.py
├── adapter.py           # 主适配器类
├── models.py           # iCross数据模型
├── transformers.py     # 数据转换器
├── exceptions.py       # 自定义异常
├── config.py          # 配置管理
└── service.py         # 业务服务
```

#### 适配器类示例：

```python
# backend/app/integrations/ozon/adapter.py
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from ozon_api import OzonAPI
from ozon_api.exceptions import OzonAPIError

from app.core.config import settings
from .models import (
    OzonProduct,
    OzonCategory,
    OzonOrder,
    OzonInventoryItem
)
from .transformers import (
    to_ozon_product,
    from_ozon_product,
    to_ozon_order,
    from_ozon_order
)


class OzonIntegrationAdapter:
    """Ozon平台集成适配器"""
    
    def __init__(self, client_id: Optional[str] = None, api_key: Optional[str] = None):
        self.client_id = client_id or settings.OZON_CLIENT_ID
        self.api_key = api_key or settings.OZON_API_KEY
        self._api: Optional[OzonAPI] = None
        self._connected = False
        
    async def connect(self) -> bool:
        """连接到Ozon API"""
        try:
            self._api = OzonAPI(
                client_id=self.client_id,
                api_key=self.api_key
            )
            
            # 测试连接
            await self._api.get_description_category_tree()
            self._connected = True
            
            logger.info("成功连接到Ozon API")
            return True
            
        except Exception as e:
            logger.error(f"连接Ozon API失败: {str(e)}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """断开Ozon API连接"""
        if self._api:
            # OzonAPI使用上下文管理器，需要适当处理
            pass
        self._connected = False
        logger.info("已断开Ozon API连接")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    # 商品管理方法
    async def get_products(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[OzonProduct]:
        """获取Ozon商品列表"""
        if not self._connected:
            await self.connect()
        
        try:
            from ozon_api.models.product_list import ProductListRequest, ProductListFilter
            
            # 构建请求
            filter_obj = ProductListFilter(
                visibility=filters.get("visibility", "VISIBLE") if filters else "VISIBLE"
            )
            
            request = ProductListRequest(
                filter=filter_obj,
                limit=min(limit, 1000),  # Ozon API限制
                last_id=None
            )
            
            # 调用API
            response = await self._api.product_list(request)
            
            # 转换为iCross模型
            products = []
            for item in response.result.items:
                product = from_ozon_product(item)
                products.append(product)
            
            logger.info(f"成功获取{len(products)}个Ozon商品")
            return products
            
        except OzonAPIError as e:
            logger.error(f"获取Ozon商品列表失败: {e.message}")
            raise
    
    async def create_product(self, product: OzonProduct) -> Dict[str, Any]:
        """在Ozon创建商品"""
        if not self._connected:
            await self.connect()
        
        try:
            # 转换为Ozon API模型
            ozon_product = to_ozon_product(product)
            
            # 调用导入API
            result = await self._api.product_import(ozon_product)
            
            logger.info(f"成功创建Ozon商品，任务ID: {result.get('task_id')}")
            return result
            
        except OzonAPIError as e:
            logger.error(f"创建Ozon商品失败: {e.message}")
            raise
    
    async def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """更新Ozon商品"""
        # 实现商品更新逻辑
        pass
    
    async def delete_product(self, product_id: str) -> bool:
        """删除Ozon商品"""
        # 实现商品删除逻辑
        pass
    
    # 分类管理方法
    async def get_categories(self) -> List[OzonCategory]:
        """获取Ozon分类树"""
        if not self._connected:
            await self.connect()
        
        try:
            # 获取分类树
            tree_response = await self._api.get_description_category_tree()
            
            # 转换为iCross模型
            categories = []
            for category in tree_response.result:
                categories.append(OzonCategory(
                    id=category["category_id"],
                    name=category["title"],
                    parent_id=category.get("parent_id"),
                    has_children=category.get("has_children", False),
                    description=category.get("description", "")
                ))
            
            logger.info(f"成功获取{len(categories)}个Ozon分类")
            return categories
            
        except OzonAPIError as e:
            logger.error(f"获取Ozon分类失败: {e.message}")
            raise
    
    # 订单管理方法
    async def get_orders(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[OzonOrder]:
        """获取Ozon订单列表"""
        # 注意：订单API在现有库中未实现
        # 需要扩展或使用其他库
        pass
    
    async def update_order_status(
        self,
        order_id: str,
        status: str,
        tracking_number: Optional[str] = None
    ) -> bool:
        """更新订单状态"""
        pass
    
    # 库存管理方法
    async def get_inventory(self) -> List[OzonInventoryItem]:
        """获取Ozon库存信息"""
        pass
    
    async def update_inventory(
        self,
        product_id: str,
        quantity: int
    ) -> bool:
        """更新Ozon库存"""
        pass
```

### 6.3 数据模型转换

```python
# backend/app/integrations/ozon/transformers.py
from typing import Dict, Any, List
from datetime import datetime

from app.models.products import Product, ProductVariant, ProductImage
from app.models.inventory import InventoryItem
from .models import OzonProduct, OzonCategory


def to_ozon_product(product: Product) -> Dict[str, Any]:
    """将iCross产品转换为Ozon API格式"""
    # 提取主要变体
    main_variant = product.variants[0] if product.variants else None
    
    return {
        "attributes": [
            {
                "attribute_id": 85,  # 产品类型
                "values": [{"value": product.category.name if product.category else "其他"}]
            },
            {
                "attribute_id": 8229,  # 品牌
                "values": [{"value": product.brand or "无品牌"}]
            },
            # 添加更多属性...
        ],
        "barcode": main_variant.sku if main_variant else "",
        "description": product.description or "",
        "dimension_unit": "mm",
        "height": product.dimensions.height if product.dimensions else 0,
        "images": [
            {
                "file_name": image.url.split("/")[-1],
                "default": i == 0
            }
            for i, image in enumerate(product.images)
        ],
        "name": product.name,
        "offer_id": product.sku,
        "price": str(product.price),
        "vat": "0",  # 根据地区设置
        "weight": product.weight or 0,
        "weight_unit": "g",
        "width": product.dimensions.width if product.dimensions else 0,
        "depth": product.dimensions.depth if product.dimensions else 0,
    }


def from_ozon_product(ozon_data: Dict[str, Any]) -> OzonProduct:
    """将Ozon API响应转换为OzonProduct模型"""
    return OzonProduct(
        product_id=ozon_data.get("product_id"),
        offer_id=ozon_data.get("offer_id"),
        name=ozon_data.get("name", ""),
        sku=ozon_data.get("offer_id", ""),
        price=float(ozon_data.get("price", 0)),
        quantity=ozon_data.get("stock", 0),
        visibility=ozon_data.get("visibility", "INVISIBLE"),
        category_id=ozon_data.get("category_id"),
        created_at=datetime.fromisoformat(ozon_data.get("created_at")) if ozon_data.get("created_at") else None,
        updated_at=datetime.fromisoformat(ozon_data.get("updated_at")) if ozon_data.get("updated_at") else None,
        images=ozon_data.get("images", []),
        attributes=ozon_data.get("attributes", {}),
        raw_data=ozon_data  # 保留原始数据
    )


def to_ozon_category(category: OzonCategory) -> Dict[str, Any]:
    """转换分类数据"""
    return {
        "category_id": category.id,
        "title": category.name,
        "parent_id": category.parent_id,
        "has_children": category.has_children,
        "description": category.description
    }


def from_ozon_category(ozon_data: Dict[str, Any]) -> OzonCategory:
    """将Ozon分类数据转换为模型"""
    return OzonCategory(
        id=ozon_data.get("category_id"),
        name=ozon_data.get("title", ""),
        parent_id=ozon_data.get("parent_id"),
        has_children=ozon_data.get("has_children", False),
        description=ozon_data.get("description", ""),
        raw_data=ozon_data
    )
```

### 6.4 配置管理

```python
# backend/app/integrations/ozon/config.py
from typing import Optional
from pydantic import BaseModel, Field
from app.core.config import settings


class OzonConfig(BaseModel):
    """Ozon集成配置"""
    
    client_id: str = Field(default_factory=lambda: settings.OZON_CLIENT_ID)
    api_key: str = Field(default_factory=lambda: settings.OZON_API_KEY)
    api_url: str = Field(default="https://api-seller.ozon.ru")
    
    # 同步设置
    sync_interval_minutes: int = Field(default=30, ge=5, le=1440)
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: int = Field(default=5, ge=1, le=60)
    
    # 商品同步设置
    sync_products: bool = Field(default=True)
    sync_orders: bool = Field(default=True)
    sync_inventory: bool = Field(default=True)
    
    # 限制设置
    max_products_per_request: int = Field(default=1000, ge=1, le=1000)
    max_orders_per_request: int = Field(default=100, ge=1, le=1000)
    
    class Config:
        env_prefix = "OZON_"


# 全局配置实例
ozon_config = OzonConfig()
```

## 7. 定时同步任务设计

### 7.1 Celery任务定义

```python
# backend/app/integrations/ozon/tasks.py
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import shared_task
from loguru import logger

from app.core.celery import celery_app
from .adapter import OzonIntegrationAdapter
from .config import ozon_config
from app.models.products import Product
from app.models.orders import Order
from app.models.inventory import InventoryItem


@shared_task(bind=True, name="ozon.sync_products")
def sync_products_task(self) -> Dict[str, Any]:
    """同步Ozon商品到本地数据库"""
    try:
        # 创建适配器实例
        adapter = OzonIntegrationAdapter()
        
        # 在异步上下文中运行
        async def async_sync():
            async with adapter:
                # 获取Ozon商品
                ozon_products = await adapter.get_products(limit=ozon_config.max_products_per_request)
                
                # 同步到本地数据库
                synced_count = 0
                updated_count = 0
                
                for ozon_product in ozon_products:
                    # 查找现有产品
                    existing_product = await Product.find_one({"sku": ozon_product.sku})
                    
                    if existing_product:
                        # 更新现有产品
                        existing_product.name = ozon_product.name
                        existing_product.price = ozon_product.price
                        existing_product.quantity = ozon_product.quantity
                        existing_product.updated_at = datetime.utcnow()
                        await existing_product.save()
                        updated_count += 1
                    else:
                        # 创建新产品
                        new_product = Product(
                            sku=ozon_product.sku,
                            name=ozon_product.name,
                            description=ozon_product.description or "",
                            price=ozon_product.price,
                            quantity=ozon_product.quantity,
                            category_id=ozon_product.category_id,
                            source="ozon",
                            source_id=str(ozon_product.product_id),
                            raw_data=ozon_product.raw_data
                        )
                        await new_product.save()
                        synced_count += 1
                
                return {
                    "synced": synced_count,
                    "updated": updated_count,
                    "total": len(ozon_products)
                }
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_sync())
        loop.close()
        
        logger.info(f"Ozon商品同步完成: 新增{result['synced']}个, 更新{result['updated']}个")
        return result
        
    except Exception as e:
        logger.error(f"Ozon商品同步失败: {str(e)}")
        raise


@shared_task(bind=True, name="ozon.sync_orders")
def sync_orders_task(self, days_back: int = 7) -> Dict[str, Any]:
    """同步Ozon订单"""
    # 实现订单同步逻辑
    pass


@shared_task(bind=True, name="ozon.sync_inventory")
def sync_inventory_task(self) -> Dict[str, Any]:
    """同步Ozon库存"""
    # 实现库存同步逻辑
    pass


@shared_task(bind=True, name="ozon.push_inventory_updates")
def push_inventory_updates_task(self) -> Dict[str, Any]:
    """推送本地库存更新到Ozon"""
    # 实现库存推送逻辑
    pass


# 定时任务调度
celery_app.conf.beat_schedule.update({
    'ozon-sync-products-every-30-minutes': {
        'task': 'ozon.sync_products',
        'schedule': timedelta(minutes=ozon_config.sync_interval_minutes),
        'args': (),
    },
    'ozon-sync-orders-every-15-minutes': {
        'task': 'ozon.sync_orders',
        'schedule': timedelta(minutes=15),
        'args': (1,),  # 同步最近1天的订单
    },
    'ozon-sync-inventory-every-hour': {
        'task': 'ozon.sync_inventory',
        'schedule': timedelta(hours=1),
        'args': (),
    },
})
```

### 7.2 事件监听器

```python
# backend/app/integrations/ozon/listeners.py
from typing import Any
from loguru import logger

from app.events import Event, EventListener
from app.models.products import Product
from app.models.orders import Order
from app.models.inventory import InventoryItem
from .adapter import OzonIntegrationAdapter


class OzonEventListener(EventListener):
    """Ozon集成事件监听器"""
    
    def __init__(self):
        super().__init__()
        self.adapter = OzonIntegrationAdapter()
    
    async def handle_product_created(self, event: Event) -> None:
        """处理产品创建事件"""
        try:
            product: Product = event.data.get("product")
            
            if product.source == "ozon":
                # 已经是Ozon产品，不重复推送
                return
            
            # 推送到Ozon
            async with self.adapter:
                result = await self.adapter.create_product(product)
                
            logger.info(f"产品{product.sku}已推送到Ozon，任务ID: {result.get('task_id')}")
            
        except Exception as e:
            logger.error(f"推送产品到Ozon失败: {str(e)}")
    
    async def handle_product_updated(self, event: Event) -> None:
        """处理产品更新事件"""
        try:
            product: Product = event.data.get("product")
            updates: dict = event.data.get("updates", {})
            
            if product.source == "ozon" and product.source_id:
                # 更新Ozon上的产品
                async with self.adapter:
                    await self.adapter.update_product(product.source_id, updates)
                
                logger.info(f"产品{product.sku}已在Ozon更新")
                
        except Exception as e:
            logger.error(f"更新Ozon产品失败: {str(e)}")
    
    async def handle_inventory_updated(self, event: Event) -> None:
        """处理库存更新事件"""
        try:
            inventory_item: InventoryItem = event.data.get("inventory_item")
            product: Product = await Product.find_one({"sku": inventory_item.sku})
            
            if product and product.source == "ozon" and product.source_id:
                # 推送库存更新到Ozon
                async with self.adapter:
                    await self.adapter.update_inventory(
                        product.source_id,
                        inventory_item.quantity
                    )
                
                logger.info(f"产品{product.sku}库存已更新到Ozon: {inventory_item.quantity}")
                
        except Exception as e:
            logger.error(f"更新Ozon库存失败: {str(e)}")
    
    async def handle_order_created(self, event: Event) -> None:
        """处理订单创建事件"""
        # 如果需要将本地订单同步到Ozon，可以在这里实现
        pass


# 注册事件监听器
ozon_event_listener = OzonEventListener()
```

## 8. API路由设计

### 8.1 Ozon集成API端点

```python
# backend/app/api/v1/endpoints/ozon.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.users import User
from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.tasks import (
    sync_products_task,
    sync_orders_task,
    sync_inventory_task
)

router = APIRouter(prefix="/ozon", tags=["ozon"])


class OzonSyncRequest(BaseModel):
    """Ozon同步请求"""
    sync_type: str = Field(..., description="同步类型: products, orders, inventory")
    force: bool = Field(default=False, description="强制同步")
    days_back: Optional[int] = Field(default=7, description="回溯天数（仅订单）")


class OzonSyncResponse(BaseModel):
    """Ozon同步响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="消息")


class OzonProductResponse(BaseModel):
    """Ozon产品响应"""
    product_id: str
    offer_id: str
    name: str
    price: float
    quantity: int
    visibility: str
    category_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@router.get("/test-connection", response_model=Dict[str, Any])
async def test_ozon_connection(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """测试Ozon API连接"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以测试连接"
        )
    
    try:
        adapter = OzonIntegrationAdapter()
        connected = await adapter.connect()
        
        if connected:
            # 获取分类树作为连接测试
            categories = await adapter.get_categories()
            
            return {
                "connected": True,
                "categories_count": len(categories),
                "message": "成功连接到Ozon API"
            }
        else:
            return {
                "connected": False,
                "message": "无法连接到Ozon API"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接测试失败: {str(e)}"
        )


@router.post("/sync", response_model=OzonSyncResponse)
async def trigger_ozon_sync(
    request: OzonSyncRequest,
    current_user: User = Depends(get_current_user)
) -> OzonSyncResponse:
    """触发Ozon数据同步"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以触发同步"
        )
    
    try:
        if request.sync_type == "products":
            task = sync_products_task.apply_async(args=(request.force,))
        elif request.sync_type == "orders":
            task = sync_orders_task.apply_async(args=(request.days_back, request.force))
        elif request.sync_type == "inventory":
            task = sync_inventory_task.apply_async(args=(request.force,))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的同步类型: {request.sync_type}"
            )
        
        return OzonSyncResponse(
            task_id=task.id,
            status=task.status,
            message=f"已启动{request.sync_type}同步任务"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动同步任务失败: {str(e)}"
        )


@router.get("/products", response_model=List[OzonProductResponse])
async def get_ozon_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=100, ge=1, le=1000),
    visibility: Optional[str] = Query(default=None, description="商品可见性"),
    current_user: User = Depends(get_current_user)
) -> List[OzonProductResponse]:
    """获取Ozon商品列表"""
    try:
        adapter = OzonIntegrationAdapter()
        
        async with adapter:
            filters = {}
            if visibility:
                filters["visibility"] = visibility
            
            products = await adapter.get_products(
                page=page,
                limit=limit,
                filters=filters
            )
            
            # 转换为响应模型
            return [
                OzonProductResponse(
                    product_id=str(p.product_id),
                    offer_id=p.offer_id,
                    name=p.name,
                    price=p.price,
                    quantity=p.quantity,
                    visibility=p.visibility,
                    category_id=str(p.category_id) if p.category_id else None,
                    created_at=p.created_at.isoformat() if p.created_at else None,
                    updated_at=p.updated_at.isoformat() if p.updated_at else None
                )
                for p in products
            ]
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Ozon商品失败: {str(e)}"
        )


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_ozon_categories(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """获取Ozon分类树"""
    try:
        adapter = OzonIntegrationAdapter()
        
        async with adapter:
            categories = await adapter.get_categories()
            
            return [
                {
                    "id": str(cat.id),
                    "name": cat.name,
                    "parent_id": str(cat.parent_id) if cat.parent_id else None,
                    "has_children": cat.has_children,
                    "description": cat.description
                }
                for cat in categories
            ]
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Ozon分类失败: {str(e)}"
        )


@router.get("/sync-status/{task_id}")
async def get_sync_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取同步任务状态"""
    from celery.result import AsyncResult
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看任务状态"
        )
    
    task_result = AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "successful": task_result.successful() if task_result.ready() else None
    }
```

## 9. 监控与日志

### 9.1 监控指标

```python
# backend/app/integrations/ozon/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from typing import Optional, Dict, Any

# 请求指标
OZON_API_REQUESTS = Counter(
    'ozon_api_requests_total',
    'Total Ozon API requests',
    ['method', 'endpoint', 'status']
)

OZON_API_REQUEST_DURATION = Histogram(
    'ozon_api_request_duration_seconds',
    'Ozon API request duration',
    ['method', 'endpoint']
)

# 同步指标
OZON_SYNC_PRODUCTS = Counter(
    'ozon_sync_products_total',
    'Total products synced from Ozon',
    ['status']
)

OZON_SYNC_ORDERS = Counter(
    'ozon_sync_orders_total',
    'Total orders synced from Ozon',
    ['status']
)

# 错误指标
OZON_API_ERRORS = Counter(
    'ozon_api_errors_total',
    'Total Ozon API errors',
    ['error_type']
)

# 连接状态
OZON_CONNECTION_STATUS = Gauge(
    'ozon_connection_status',
    'Ozon API connection status (1=connected, 0=disconnected)'
)
```

### 9.2 日志配置

```python
# 在适配器中添加详细日志
import logging
from loguru import logger

# 配置Ozon API日志
ozon_logger = logging.getLogger('ozon_api')
ozon_logger.setLevel(logging.INFO)

# 添加文件处理器
handler = logging.FileHandler('logs/ozon_api.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
ozon_logger.addHandler(handler)

# 使用loguru的装饰器
def log_ozon_api_call(func):
    """记录Ozon API调用的装饰器"""
    async def wrapper(*args, **kwargs):
        logger.info(f"调用Ozon API: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Ozon API调用成功: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Ozon API调用失败: {func.__name__}, 错误: {str(e)}")
            raise
    return wrapper
```

## 10. 测试策略

### 10.1 单元测试

```python
# tests/integrations/test_ozon_adapter.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.integrations.ozon.models import OzonProduct, OzonCategory


class TestOzonIntegrationAdapter:
    
    @pytest.fixture
    def adapter(self):
        return OzonIntegrationAdapter(
            client_id="test-client-id",
            api_key="test-api-key"
        )
    
    @pytest.fixture
    def mock_ozon_api(self):
        with patch('app.integrations.ozon.adapter.OzonAPI') as mock:
            api_instance = AsyncMock()
            mock.return_value = api_instance
            yield api_instance
    
    @pytest.mark.asyncio
    async def test_connect_success(self, adapter, mock_ozon_api):
        """测试成功连接"""
        mock_ozon_api.get_description_category_tree = AsyncMock()
        
        connected = await adapter.connect()
        
        assert connected is True
        assert adapter._connected is True
        mock_ozon_api.get_description_category_tree.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, adapter, mock_ozon_api):
        """测试连接失败"""
        mock_ozon_api.get_description_category_tree = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        connected = await adapter.connect()
        
        assert connected is False
        assert adapter._connected is False
    
    @pytest.mark.asyncio
    async def test_get_products(self, adapter, mock_ozon_api):
        """测试获取商品列表"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.result.items = [
            {
                "product_id": 12345,
                "offer_id": "TEST001",
                "name": "测试商品",
                "price": 100.0,
                "stock": 50,
                "visibility": "VISIBLE",
                "category_id": 17031234,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        ]
        
        mock_ozon_api.product_list = AsyncMock(return_value=mock_response)
        adapter._connected = True
        adapter._api = mock_ozon_api
        
        products = await adapter.get_products(limit=10)
        
        assert len(products) == 1
        assert products[0].offer_id == "TEST001"
        assert products[0].name == "测试商品"
        mock_ozon_api.product_list.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_categories(self, adapter, mock_ozon_api):
        """测试获取分类"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.result = [
            {
                "category_id": 17031234,
                "title": "电子产品",
                "parent_id": None,
                "has_children": True,
                "description": "电子设备分类"
            }
        ]
        
        mock_ozon_api.get_description_category_tree = AsyncMock(return_value=mock_response)
        adapter._connected = True
        adapter._api = mock_ozon_api
        
        categories = await adapter.get_categories()
        
        assert len(categories) == 1
        assert categories[0].name == "电子产品"
        assert categories[0].has_children is True
```

### 10.2 集成测试

```python
# tests/integrations/test_ozon_integration.py
import pytest
import asyncio
from datetime import datetime, timedelta

from app.integrations.ozon.adapter import OzonIntegrationAdapter
from app.models.products import Product


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_ozon_connection():
    """真实Ozon API连接测试（需要有效凭证）"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    
    if not client_id or not api_key:
        pytest.skip("Ozon API凭证未设置")
    
    adapter = OzonIntegrationAdapter(client_id=client_id, api_key=api_key)
    
    try:
        # 测试连接
        connected = await adapter.connect()
        assert connected is True
        
        # 测试获取分类（通常不需要特殊权限）
        categories = await adapter.get_categories()
        assert isinstance(categories, list)
        
        # 测试获取商品（限制数量以减少API调用）
        products = await adapter.get_products(limit=10)
        assert isinstance(products, list)
        
        await adapter.disconnect()
        
    except Exception as e:
        pytest.fail(f"Ozon集成测试失败: {str(e)}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_product_sync_flow():
    """产品同步流程测试"""
    # 模拟从Ozon获取数据并同步到本地数据库的完整流程
    pass
```

## 11. 部署与运维

### 11.1 环境变量配置

```env
# Ozon集成配置
OZON_CLIENT_ID=your-client-id
OZON_API_KEY=your-api-key
OZON_API_URL=https://api-seller.ozon.ru
OZON_SYNC_INTERVAL_MINUTES=30
OZON_MAX_RETRIES=3
OZON_RETRY_DELAY_SECONDS=5
OZON_SYNC_PRODUCTS=true
OZON_SYNC_ORDERS=true
OZON_SYNC_INVENTORY=true
```

### 11.2 Docker配置

```dockerfile
# 在Dockerfile中添加Ozon API依赖
RUN pip install aiohttp pydantic tenacity loguru

# 复制Ozon API库
COPY python-ozon-api-main /app/python-ozon-api-main
RUN pip install -e /app/python-ozon-api-main
```

### 11.3 Kubernetes配置

```yaml
# kubernetes/configmaps/ozon-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ozon-config
data:
  OZON_CLIENT_ID: "{{ .Values.ozon.clientId }}"
  OZON_API_KEY: "{{ .Values.ozon.apiKey }}"
  OZON_SYNC_INTERVAL_MINUTES: "30"
  OZON_MAX_RETRIES: "3"
```

### 11.4 健康检查端点

```python
# backend/app/api/health.py
@router.get("/ozon")
async def ozon_health():
    """Ozon集成健康检查"""
    try:
        adapter = OzonIntegrationAdapter()
        connected = await adapter.connect()
        
        return {
            "status": "healthy" if connected else "unhealthy",
            "connected": connected,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

## 12. 故障排除

### 12.1 常见问题

#### 问题1：API认证失败
**症状**：收到401或403错误
**解决方案**：
1. 检查`OZON_CLIENT_ID`和`OZON_API_KEY`环境变量
2. 验证API密钥是否有效且未过期
3. 检查IP白名单设置

#### 问题2：请求限流
**症状**：收到429错误或请求被拒绝
**解决方案**：
1. 降低请求频率
2. 实现指数退避重试机制
3. 批量处理请求，减少API调用次数

#### 问题3：数据同步失败
**症状**：同步任务失败或数据不一致
**解决方案**：
1. 检查网络连接和防火墙设置
2. 验证数据格式是否符合Ozon API要求
3. 查看详细错误日志

#### 问题4：内存泄漏
**症状**：内存使用持续增长
**解决方案**：
1. 确保正确关闭aiohttp会话
2. 使用连接池
3. 定期重启工作进程

### 12.2 调试工具

```python
# debug_ozon.py - Ozon集成调试工具
import asyncio
import json
from datetime import datetime
from ozon_api import OzonAPI
from dotenv import load_dotenv
import os

load_dotenv()

async def debug_ozon_api():
    """调试Ozon API连接和功能"""
    client_id = os.getenv("OZON_CLIENT_ID")
    api_key = os.getenv("OZON_API_KEY")
    
    if not client_id or not api_key:
        print("错误: 未设置Ozon API凭证")
        return
    
    print(f"开始调试Ozon API...")
    print(f"客户端ID: {client_id[:10]}...")
    print(f"API密钥: {api_key[:10]}...")
    
    try:
        async with OzonAPI(client_id=client_id, api_key=api_key) as api:
            # 测试连接
            print("1. 测试API连接...")
            categories = await api.get_description_category_tree()
            print(f"   成功! 获取到{len(categories.result)}个分类")
            
            # 测试商品列表
            print("2. 测试商品列表API...")
            from ozon_api.models.product_list import ProductListRequest, ProductListFilter
            
            request = ProductListRequest(
                filter=ProductListFilter(),
                limit=10
            )
            products = await api.product_list(request)
            print(f"   成功! 获取到{len(products.result.items)}个商品")
            
            # 测试错误处理
            print("3. 测试错误处理...")
            try:
                # 故意发送无效请求
                invalid_request = ProductListRequest(
                    filter=ProductListFilter(),
                    limit=5000  # 超过限制
                )
                await api.product_list(invalid_request)
            except Exception as e:
                print(f"   成功捕获错误: {type(e).__name__}: {str(e)}")
            
            print("\n调试完成!")
            
    except Exception as e:
        print(f"调试失败: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_ozon_api())
```

## 13. 扩展与自定义

### 13.1 添加新的API方法

```python
# backend/app/integrations/ozon/extensions.py
from ozon_api.base import OzonAPIBase
from typing import List, Dict, Any
from pydantic import BaseModel


class OzonOrderRequest(BaseModel):
    """Ozon订单请求模型"""
    date_from: str
    date_to: str
    status: str = "all"
    page: int = 1
    page_size: int = 100


class OzonOrderResponse(BaseModel):
    """Ozon订单响应模型"""
    order_id: str
    order_number: str
    status: str
    created_at: str
    total_amount: float
    items: List[Dict[str, Any]]


class ExtendedOzonAPI(OzonAPIBase):
    """扩展的Ozon API客户端"""
    
    async def get_orders(self, request: OzonOrderRequest) -> List[OzonOrderResponse]:
        """获取订单列表（需要Ozon订单API端点）"""
        # 注意：现有库中可能没有订单API
        # 需要根据Ozon文档实现
        
        data = await self._request(
            method="post",
            api_version="v3",
            endpoint="order/list",  # 假设的端点
            json=request.model_dump()
        )
        
        orders = []
        for order_data in data.get("orders", []):
            orders.append(OzonOrderResponse(**order_data))
        
        return orders
    
    async def update_order_status(
        self,
        order_id: str,
        status: str,
        tracking_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新订单状态"""
        payload = {
            "order_id": order_id,
            "status": status
        }
        
        if tracking_number:
            payload["tracking_number"] = tracking_number
        
        data = await self._request(
            method="post",
            api_version="v2",
            endpoint="order/status/update",
            json=payload
        )
        
        return data
```

### 13.2 自定义重试策略

```python
# backend/app/integrations/ozon/retry.py
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    RetryCallState
)
from typing import Any
from loguru import logger


def log_retry_attempt(retry_state: RetryCallState) -> None:
    """记录重试尝试"""
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        logger.warning(
            f"重试 {retry_state.attempt_number}/{retry_state.retry_object.stop.max_attempt_number}: "
            f"{type(exception).__name__}: {str(exception)}"
        )


# 自定义重试装饰器
ozon_retry = retry(
    retry=retry_if_exception_type((TimeoutError, ConnectionError, OSError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30) + wait_random(0, 2),
    before_sleep=log_retry_attempt,
    reraise=True
)


class OzonRetryMixin:
    """Ozon重试混合类"""
    
    @ozon_retry
    async def _request_with_retry(self, *args, **kwargs) -> Any:
        """带重试的请求方法"""
        return await self._request(*args, **kwargs)
```

## 14. 性能优化

### 14.1 连接池优化

```python
# backend/app/integrations/ozon/pool.py
import asyncio
from typing import Optional, List
from aiohttp import ClientSession, TCPConnector
from loguru import logger


class OzonConnectionPool:
    """Ozon连接池"""
    
    def __init__(
        self,
        client_id: str,
        api_key: str,
        pool_size: int = 10,
        ttl: int = 300
    ):
        self.client_id = client_id
        self.api_key = api_key
        self.pool_size = pool_size
        self.ttl = ttl  # 连接存活时间（秒）
        
        self._pool: List[ClientSession] = []
        self._lock = asyncio.Lock()
    
    async def get_session(self) -> ClientSession:
        """从池中获取会话"""
        async with self._lock:
            if self._pool:
                session = self._pool.pop()
                logger.debug(f"从连接池获取会话，剩余: {len(self._pool)}")
                return session
            
            # 创建新会话
            session = ClientSession(
                headers={
                    "Client-Id": self.client_id,
                    "Api-Key": self.api_key
                },
                connector=TCPConnector(limit=100)  # 提高连接限制
            )
            logger.debug("创建新的Ozon API会话")
            return session
    
    async def release_session(self, session: ClientSession) -> None:
        """释放会话到池中"""
        async with self._lock:
            if len(self._pool) < self.pool_size:
                self._pool.append(session)
                logger.debug(f"会话已释放到连接池，当前大小: {len(self._pool)}")
            else:
                await session.close()
                logger.debug("连接池已满，关闭会话")
    
    async def cleanup(self) -> None:
        """清理连接池"""
        async with self._lock:
            for session in self._pool:
                if not session.closed:
                    await session.close()
            self._pool.clear()
            logger.info("Ozon连接池已清理")
```

### 14.2 批量处理优化

```python
# backend/app/integrations/ozon/batch.py
import asyncio
from typing import List, Any, Callable, TypeVar, Optional
from itertools import islice
from loguru import logger

T = TypeVar('T')
R = TypeVar('R')


class BatchProcessor:
    """批量处理器"""
    
    def __init__(
        self,
        batch_size: int = 100,
        max_concurrent: int = 5,
        delay_between_batches: float = 1.0
    ):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.delay_between_batches = delay_between_batches
    
    async def process_batch(
        self,
        items: List[T],
        processor: Callable[[List[T]], Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """批量处理项目"""
        total_items = len(items)
        results = []
        
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_chunk(chunk: List[T], chunk_index: int) -> Any:
            async with semaphore:
                try:
                    result = await processor(chunk)
                    
                    if progress_callback:
                        progress_callback(chunk_index * self.batch_size, total_items)
                    
                    return result
                except Exception as e:
                    logger.error(f"处理批次{chunk_index}失败: {str(e)}")
                    raise
        
        # 分批次处理
        tasks = []
        for i, start in enumerate(range(0, total_items, self.batch_size)):
            chunk = list(islice(items, start, start + self.batch_size))
            
            if i > 0 and self.delay_between_batches > 0:
                await asyncio.sleep(self.delay_between_batches)
            
            task = asyncio.create_task(process_chunk(chunk, i))
            tasks.append(task)
        
        # 等待所有任务完成
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for result in chunk_results:
            if isinstance(result, Exception):
                logger.error(f"批次处理失败: {str(result)}")
            else:
                results.extend(result)
        
        return results
```

## 15. 安全考虑

### 15.1 API密钥安全

```python
# backend/app/core/security/ozon_security.py
import os
from typing import Optional
from cryptography.fernet import Fernet
from loguru import logger


class OzonCredentialsManager:
    """Ozon凭证管理器"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("未设置加密密钥")
        
        self.cipher = Fernet(self.encryption_key.encode())
    
    def encrypt_credentials(self, client_id: str, api_key: str) -> tuple[str, str]:
        """加密Ozon凭证"""
        encrypted_client_id = self.cipher.encrypt(client_id.encode()).decode()
        encrypted_api_key = self.cipher.encrypt(api_key.encode()).decode()
        
        logger.debug("Ozon凭证已加密")
        return encrypted_client_id, encrypted_api_key
    
    def decrypt_credentials(self, encrypted_client_id: str, encrypted_api_key: str) -> tuple[str, str]:
        """解密Ozon凭证"""
        try:
            client_id = self.cipher.decrypt(encrypted_client_id.encode()).decode()
            api_key = self.cipher.decrypt(encrypted_api_key.encode()).decode()
            
            logger.debug("Ozon凭证已解密")
            return client_id, api_key
        except Exception as e:
            logger.error(f"解密Ozon凭证失败: {str(e)}")
            raise
    
    def rotate_credentials(self, old_encrypted: tuple[str, str], new_client_id: str, new_api_key: str) -> tuple[str, str]:
        """轮换Ozon凭证"""
        # 验证旧凭证
        old_client_id, old_api_key = self.decrypt_credentials(*old_encrypted)
        
        # 加密新凭证
        new_encrypted = self.encrypt_credentials(new_client_id, new_api_key)
        
        logger.info("Ozon凭证已轮换")
        return new_encrypted
```

### 15.2 访问控制

```python
# backend/app/integrations/ozon/access_control.py
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel


class OzonAccessLevel(Enum):
    """Ozon访问级别"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


class OzonAccessControl(BaseModel):
    """Ozon访问控制"""
    
    tenant_id: str
    user_id: Optional[str] = None
    access_level: OzonAccessLevel = OzonAccessLevel.READ_ONLY
    allowed_operations: List[str] = []
    ip_whitelist: Optional[List[str]] = None
    
    def can_access(self, operation: str, ip_address: Optional[str] = None) -> bool:
        """检查是否有权限执行操作"""
        # 检查IP白名单
        if self.ip_whitelist and ip_address:
            if ip_address not in self.ip_whitelist:
                return False
        
        # 检查操作权限
        if operation not in self.allowed_operations:
            return False
        
        return True
```

## 16. 更新与维护

### 16.1 版本兼容性

| Ozon API版本 | 库版本 | 兼容性 | 备注 |
|-------------|--------|--------|------|
| v3 | 1.6.1 | ✅ 完全支持 | 主要API版本 |
| v4 | 1.6.1 | ⚠️ 部分支持 | 仅限部分端点 |
| v2 | 1.6.1 | ✅ 完全支持 | 向后兼容 |
| v1 | 1.6.1 | ✅ 完全支持 | 基础功能 |

### 16.2 更新策略

```python
# backend/app/integrations/ozon/updater.py
import asyncio
from typing import Dict, Any
from datetime import datetime
from loguru import logger


class OzonIntegrationUpdater:
    """Ozon集成更新器"""
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """检查Ozon API更新"""
        # 这里可以实现检查API变更的逻辑
        # 例如：检查API文档、版本号变化等
        
        return {
            "last_checked": datetime.utcnow().isoformat(),
            "update_available": False,
            "current_version": "1.6.1",
            "latest_version": "1.6.1",
            "changes": []
        }
    
    async def apply_updates(self) -> bool:
        """应用更新"""
        try:
            # 更新Ozon API库
            # 这可能需要重新安装包或更新代码
            
            logger.info("开始更新Ozon集成...")
            
            # 模拟更新过程
            await asyncio.sleep(2)
            
            logger.info("Ozon集成更新完成")
            return True
            
        except Exception as e:
            logger.error(f"更新Ozon集成失败: {str(e)}")
            return False
```

---

## 附录

### A. Ozon API官方文档
- [Ozon Seller API文档](https://docs.ozon.ru/api/seller/)
- [API参考](https://docs.ozon.ru/api/seller/#section/Obzornye-svedeniya)
- [错误代码](https://docs.ozon.ru/api/seller/#section/Spisok-oshibok)

### B. 相关工具
- [Ozon API测试工具](https://seller.ozon.ru/app/api-test)
- [Postman集合](https://www.postman.com/ozonworkspace/ozon-seller-api)
- [API监控面板](https://seller.ozon.ru/app/analytics/api)

### C. 支持与联系
- **技术支持**: integration-support@icross.com
- **紧急问题**: +86 123 4567 8900
- **文档反馈**: docs-feedback@icross.com

### D. 更新日志

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-02-18 | 初始版本，完整集成指南 |
| v0.9 | 2026-02-17 | 初稿完成，包含核心集成方案 |

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-02-18 | 完整Ozon API集成指南 | AI Assistant |

*本文档将随着Ozon API变更和集成需求演进持续更新。*