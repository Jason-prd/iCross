# iCross API 设计文档

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v2.0 |
| **最后更新** | 2026-02-18 |
| **API版本** | v1.0 |
| **文档负责人** | 后端架构师 |

## 1. API 设计原则

### 1.1 RESTful API 设计
- **资源导向**：使用名词复数表示资源，动词通过HTTP方法表达
- **版本管理**：URL路径包含版本号 `/api/v1/`
- **状态码规范**：正确使用HTTP状态码（200成功，400客户端错误，500服务器错误）
- **错误处理**：统一错误响应格式，包含错误代码和消息
- **分页查询**：支持limit/offset分页，默认limit=20，最大limit=100
- **字段选择**：支持fields参数选择返回字段
- **排序支持**：支持sort参数指定排序字段和方向

### 1.2 API 认证与授权
- **认证方式**：JWT (JSON Web Token) Bearer Token
- **Token获取**：`POST /api/v1/auth/login` 返回access_token和refresh_token
- **Token刷新**：`POST /api/v1/auth/refresh` 使用refresh_token获取新access_token
- **Token过期**：access_token 15分钟过期，refresh_token 7天过期
- **权限控制**：基于角色的访问控制 (RBAC)
- **API限流**：基于用户或IP的速率限制（1000次/小时/用户）

### 1.3 请求与响应格式
- **请求头**：
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
  - `X-Request-ID`：请求唯一标识，用于追踪
- **响应头**：
  - `Content-Type: application/json`
  - `X-Request-ID`：响应请求ID
  - `X-RateLimit-Limit`：限流限制
  - `X-RateLimit-Remaining`：剩余请求次数
- **时间格式**：ISO 8601格式 `YYYY-MM-DDTHH:mm:ssZ`
- **货币格式**：使用最小单位（分），整数存储

## 2. 错误处理

### 2.1 错误响应格式
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "email",
      "reason": "邮箱格式不正确"
    },
    "request_id": "req_1234567890abcdef",
    "timestamp": "2026-02-18T10:30:00Z"
  }
}
```

### 2.2 错误代码分类
| 错误类别 | HTTP状态码 | 错误代码前缀 | 示例 |
|----------|------------|--------------|------|
| **客户端错误** | 400 | `VALIDATION_` | `VALIDATION_REQUIRED`, `VALIDATION_INVALID_EMAIL` |
| **认证错误** | 401 | `AUTH_` | `AUTH_INVALID_TOKEN`, `AUTH_EXPIRED_TOKEN` |
| **授权错误** | 403 | `PERMISSION_` | `PERMISSION_DENIED`, `PERMISSION_INSUFFICIENT` |
| **资源未找到** | 404 | `NOT_FOUND_` | `NOT_FOUND_USER`, `NOT_FOUND_ORDER` |
| **冲突错误** | 409 | `CONFLICT_` | `CONFLICT_DUPLICATE_EMAIL`, `CONFLICT_RESOURCE_EXISTS` |
| **速率限制** | 429 | `RATE_LIMIT_` | `RATE_LIMIT_EXCEEDED` |
| **服务器错误** | 500 | `INTERNAL_` | `INTERNAL_SERVER_ERROR`, `INTERNAL_DATABASE_ERROR` |
| **服务不可用** | 503 | `SERVICE_` | `SERVICE_UNAVAILABLE`, `SERVICE_MAINTENANCE` |

### 2.3 常见错误代码
| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| `VALIDATION_REQUIRED` | 400 | 必填字段缺失 |
| `VALIDATION_INVALID_EMAIL` | 400 | 邮箱格式无效 |
| `VALIDATION_INVALID_PHONE` | 400 | 手机号格式无效 |
| `VALIDATION_OUT_OF_RANGE` | 400 | 数值超出范围 |
| `AUTH_INVALID_CREDENTIALS` | 401 | 用户名或密码错误 |
| `AUTH_INVALID_TOKEN` | 401 | Token无效 |
| `AUTH_EXPIRED_TOKEN` | 401 | Token已过期 |
| `PERMISSION_DENIED` | 403 | 没有访问权限 |
| `NOT_FOUND_RESOURCE` | 404 | 资源不存在 |
| `CONFLICT_DUPLICATE` | 409 | 资源重复 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |

## 3. 认证服务 API

### 3.1 用户认证
#### POST /api/v1/auth/login
用户登录，获取访问令牌。

**请求体**：
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**响应体**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "张三",
    "role": "admin",
    "team_id": "team_456"
  }
}
```

#### POST /api/v1/auth/register
用户注册。

**请求体**：
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "张三",
  "phone": "+8613800138000",
  "company_name": "示例公司"
}
```

**响应体**：同登录响应。

#### POST /api/v1/auth/refresh
刷新访问令牌。

**请求体**：
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应体**：同登录响应（仅返回新的token）。

#### POST /api/v1/auth/logout
用户登出。

**请求头**：`Authorization: Bearer <token>`

**响应体**：
```json
{
  "message": "登出成功"
}
```

### 3.2 用户管理
#### GET /api/v1/users/me
获取当前用户信息。

**响应体**：
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "张三",
  "phone": "+8613800138000",
  "role": "admin",
  "team_id": "team_456",
  "created_at": "2026-02-18T10:30:00Z",
  "updated_at": "2026-02-18T10:30:00Z"
}
```

#### PUT /api/v1/users/me
更新当前用户信息。

**请求体**：
```json
{
  "name": "李四",
  "phone": "+8613800138001"
}
```

**响应体**：更新后的用户信息。

#### POST /api/v1/users/password
修改密码。

**请求体**：
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

### 3.3 团队管理
#### GET /api/v1/teams
获取当前用户所属团队。

**响应体**：
```json
{
  "id": "team_456",
  "name": "示例团队",
  "owner_id": "user_123",
  "plan": "pro",
  "member_count": 5,
  "created_at": "2026-02-18T10:30:00Z"
}
```

#### GET /api/v1/teams/members
获取团队成员列表。

**查询参数**：
- `page`：页码，默认1
- `limit`：每页数量，默认20
- `role`：按角色筛选

**响应体**：
```json
{
  "items": [
    {
      "id": "user_123",
      "email": "user@example.com",
      "name": "张三",
      "role": "admin",
      "joined_at": "2026-02-18T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "limit": 20,
    "pages": 1
  }
}
```

#### POST /api/v1/teams/members/invite
邀请团队成员。

**请求体**：
```json
{
  "email": "newuser@example.com",
  "role": "member",
  "message": "欢迎加入我们的团队"
}
```

#### DELETE /api/v1/teams/members/{user_id}
移除团队成员。

## 4. 店铺服务 API

### 4.1 店铺管理
#### GET /api/v1/shops
获取店铺列表。

**查询参数**：
- `platform`：按平台筛选（amazon, ozon, shopify等）
- `status`：按状态筛选（connected, disconnected, error）
- `page`, `limit`：分页参数

**响应体**：
```json
{
  "items": [
    {
      "id": "shop_789",
      "name": "我的亚马逊店铺",
      "platform": "amazon",
      "platform_shop_id": "A123456789",
      "status": "connected",
      "last_sync_at": "2026-02-18T10:30:00Z",
      "created_at": "2026-02-18T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### POST /api/v1/shops
添加新店铺。

**请求体**：
```json
{
  "name": "我的Ozon店铺",
  "platform": "ozon",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "settings": {
    "sync_interval": 300,
    "auto_sync": true
  }
}
```

#### GET /api/v1/shops/{shop_id}
获取店铺详情。

#### PUT /api/v1/shops/{shop_id}
更新店铺信息。

#### DELETE /api/v1/shops/{shop_id}
删除店铺。

#### POST /api/v1/shops/{shop_id}/sync
手动触发店铺同步。

**查询参数**：
- `type`：同步类型（full, incremental, orders, products, inventory）

**响应体**：
```json
{
  "task_id": "task_abc123",
  "status": "queued",
  "message": "同步任务已排队"
}
```

#### GET /api/v1/shops/{shop_id}/sync-status
获取同步状态。

### 4.2 店铺统计
#### GET /api/v1/shops/{shop_id}/statistics
获取店铺统计信息。

**查询参数**：
- `period`：统计周期（today, yesterday, last_7_days, last_30_days, custom）
- `start_date`, `end_date`：自定义日期范围

**响应体**：
```json
{
  "period": {
    "start": "2026-02-11",
    "end": "2026-02-18"
  },
  "orders": {
    "total": 150,
    "completed": 120,
    "pending": 20,
    "cancelled": 10,
    "revenue": 1250000
  },
  "products": {
    "total": 500,
    "active": 450,
    "out_of_stock": 30,
    "inactive": 20
  },
  "customers": {
    "total": 100,
    "new": 20,
    "returning": 80
  }
}
```

## 5. 商品服务 API

### 5.1 商品管理
#### GET /api/v1/products
获取商品列表。

**查询参数**：
- `shop_id`：按店铺筛选
- `platform`：按平台筛选
- `category_id`：按分类筛选
- `status`：按状态筛选（active, inactive, out_of_stock, draft）
- `search`：关键词搜索（标题、SKU）
- `min_price`, `max_price`：价格范围
- `has_image`：是否有图片
- `sort`：排序字段（created_at, price, sales）
- `order`：排序方向（asc, desc）

**响应体**：
```json
{
  "items": [
    {
      "id": "product_123",
      "shop_id": "shop_789",
      "platform": "amazon",
      "platform_product_id": "B08N5WRWNW",
      "sku": "SKU001",
      "title": "无线蓝牙耳机",
      "description": "高音质无线蓝牙耳机...",
      "price": 1999,
      "original_price": 2999,
      "currency": "CNY",
      "stock": 50,
      "status": "active",
      "images": ["https://.../image1.jpg"],
      "variants": [
        {
          "id": "variant_456",
          "sku": "SKU001-BLACK",
          "attributes": {"color": "black", "size": "M"},
          "price": 1999,
          "stock": 25
        }
      ],
      "created_at": "2026-02-18T10:30:00Z",
      "updated_at": "2026-02-18T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### POST /api/v1/products
创建新商品。

**请求体**：
```json
{
  "shop_id": "shop_789",
  "sku": "SKU001",
  "title": "无线蓝牙耳机",
  "description": "高音质无线蓝牙耳机...",
  "price": 1999,
  "stock": 50,
  "category_id": "cat_123",
  "attributes": {
    "brand": "Apple",
    "color": "white",
    "weight": "200g"
  },
  "images": ["https://.../image1.jpg"],
  "variants": [
    {
      "sku": "SKU001-BLACK",
      "attributes": {"color": "black", "size": "M"},
      "price": 1999,
      "stock": 25
    }
  ]
}
```

#### GET /api/v1/products/{product_id}
获取商品详情。

#### PUT /api/v1/products/{product_id}
更新商品信息。

#### DELETE /api/v1/products/{product_id}
删除商品。

#### POST /api/v1/products/batch-update
批量更新商品。

**请求体**：
```json
{
  "product_ids": ["product_123", "product_456"],
  "updates": {
    "price": 1899,
    "status": "active"
  }
}
```

### 5.2 商品分类
#### GET /api/v1/categories
获取分类列表。

#### POST /api/v1/categories
创建分类。

#### PUT /api/v1/categories/{category_id}
更新分类。

#### DELETE /api/v1/categories/{category_id}
删除分类。

### 5.3 商品同步
#### POST /api/v1/products/sync
同步商品数据。

**请求体**：
```json
{
  "shop_id": "shop_789",
  "type": "incremental",
  "force": false
}
```

#### GET /api/v1/products/sync-status/{task_id}
获取同步任务状态。

## 6. 订单服务 API

### 6.1 订单管理
#### GET /api/v1/orders
获取订单列表。

**查询参数**：
- `shop_id`：按店铺筛选
- `platform`：按平台筛选
- `status`：按状态筛选（pending, paid, shipped, completed, cancelled, refunded）
- `customer_id`：按客户筛选
- `date_from`, `date_to`：订单日期范围
- `min_amount`, `max_amount`：订单金额范围

**响应体**：
```json
{
  "items": [
    {
      "id": "order_123",
      "shop_id": "shop_789",
      "platform": "amazon",
      "platform_order_id": "171-1234567-1234567",
      "order_number": "ORD-20260218-001",
      "customer_id": "customer_456",
      "customer": {
        "name": "张三",
        "email": "customer@example.com",
        "phone": "+8613800138000"
      },
      "shipping_address": {
        "name": "张三",
        "phone": "+8613800138000",
        "address_line1": "北京市朝阳区",
        "city": "北京",
        "state": "北京",
        "country": "CN",
        "postal_code": "100000"
      },
      "status": "paid",
      "total_amount": 3998,
      "currency": "CNY",
      "items": [
        {
          "product_id": "product_123",
          "sku": "SKU001",
          "name": "无线蓝牙耳机",
          "quantity": 2,
          "unit_price": 1999,
          "subtotal": 3998
        }
      ],
      "shipping_method": "standard",
      "tracking_number": "SF1234567890",
      "created_at": "2026-02-18T10:30:00Z",
      "updated_at": "2026-02-18T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### GET /api/v1/orders/{order_id}
获取订单详情。

#### PUT /api/v1/orders/{order_id}/status
更新订单状态。

**请求体**：
```json
{
  "status": "shipped",
  "tracking_number": "SF1234567890",
  "carrier": "顺丰速运"
}
```

#### POST /api/v1/orders/{order_id}/cancel
取消订单。

#### POST /api/v1/orders/{order_id}/refund
退款处理。

### 6.2 订单批量操作
#### POST /api/v1/orders/batch-process
批量处理订单。

**请求体**：
```json
{
  "order_ids": ["order_123", "order_456"],
  "action": "mark_shipped",
  "parameters": {
    "tracking_number": "SF1234567890",
    "carrier": "顺丰速运"
  }
}
```

#### POST /api/v1/orders/batch-print
批量打印面单。

**请求体**：
```json
{
  "order_ids": ["order_123", "order_456"],
  "template": "standard",
  "paper_size": "A4"
}
```

**响应体**：
```json
{
  "print_task_id": "print_abc123",
  "file_url": "https://.../labels.pdf",
  "count": 2
}
```

### 6.3 订单统计
#### GET /api/v1/orders/statistics
获取订单统计。

**查询参数**：
- `period`：统计周期
- `shop_id`：按店铺筛选
- `group_by`：分组维度（day, week, month, platform, status）

**响应体**：
```json
{
  "period": {
    "start": "2026-02-11",
    "end": "2026-02-18"
  },
  "summary": {
    "total_orders": 150,
    "total_revenue": 1250000,
    "average_order_value": 8333,
    "conversion_rate": 2.5
  },
  "by_status": {
    "pending": 10,
    "paid": 30,
    "shipped": 80,
    "completed": 20,
    "cancelled": 10
  },
  "by_platform": {
    "amazon": 80,
    "ozon": 40,
    "shopify": 30
  }
}
```

## 7. 库存服务 API

### 7.1 库存管理
#### GET /api/v1/inventory
获取库存列表。

**查询参数**：
- `product_id`：按商品筛选
- `warehouse_id`：按仓库筛选
- `sku`：按SKU筛选
- `low_stock`：仅显示低库存商品（库存低于安全库存）
- `out_of_stock`：仅显示缺货商品

**响应体**：
```json
{
  "items": [
    {
      "id": "inv_123",
      "product_id": "product_123",
      "warehouse_id": "warehouse_456",
      "sku": "SKU001",
      "product_name": "无线蓝牙耳机",
      "warehouse_name": "北京仓库",
      "quantity": 50,
      "reserved_quantity": 5,
      "available_quantity": 45,
      "safety_stock": 20,
      "status": "normal",
      "last_updated": "2026-02-18T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### POST /api/v1/inventory/adjust
调整库存。

**请求体**：
```json
{
  "product_id": "product_123",
  "warehouse_id": "warehouse_456",
  "adjustment_type": "increase", // increase, decrease, set
  "quantity": 10,
  "reason": "采购入库",
  "reference_id": "po_789"
}
```

#### GET /api/v1/inventory/history/{product_id}
获取库存变更历史。

### 7.2 仓库管理
#### GET /api/v1/warehouses
获取仓库列表。

#### POST /api/v1/warehouses
创建仓库。

#### PUT /api/v1/warehouses/{warehouse_id}
更新仓库。

#### DELETE /api/v1/warehouses/{warehouse_id}
删除仓库。

### 7.3 库存预警
#### GET /api/v1/inventory/alerts
获取库存预警列表。

**查询参数**：
- `alert_type`：预警类型（low_stock, out_of_stock, excess_stock）
- `resolved`：是否已处理

**响应体**：
```json
{
  "items": [
    {
      "id": "alert_123",
      "product_id": "product_123",
      "sku": "SKU001",
      "product_name": "无线蓝牙耳机",
      "alert_type": "low_stock",
      "current_quantity": 15,
      "threshold": 20,
      "message": "库存低于安全库存",
      "created_at": "2026-02-18T10:30:00Z",
      "resolved": false
    }
  ]
}
```

#### POST /api/v1/inventory/alerts/{alert_id}/resolve
处理库存预警。

### 7.4 补货建议
#### GET /api/v1/inventory/replenishment
获取补货建议。

**查询参数**：
- `warehouse_id`：按仓库筛选
- `urgency`：紧急程度（high, medium, low）

**响应体**：
```json
{
  "items": [
    {
      "product_id": "product_123",
      "sku": "SKU001",
      "product_name": "无线蓝牙耳机",
      "current_stock": 15,
      "safety_stock": 20,
      "daily_sales": 5,
      "lead_time_days": 7,
      "suggested_quantity": 50,
      "urgency": "high",
      "reason": "库存低于安全库存，且日销较高"
    }
  ]
}
```

## 8. CRM 服务 API

### 8.1 客户管理
#### GET /api/v1/customers
获取客户列表。

**查询参数**：
- `segment_id`：按客户分组筛选
- `customer_type`：客户类型（b2b, b2c）
- `status`：客户状态（active, inactive, vip）
- `search`：关键词搜索（姓名、邮箱、电话）
- `order_count_min`, `order_count_max`：订单数量范围
- `total_spent_min`, `total_spent_max`：累计消费金额范围

**响应体**：
```json
{
  "items": [
    {
      "id": "customer_123",
      "email": "customer@example.com",
      "name": "张三",
      "phone": "+8613800138000",
      "customer_type": "b2c",
      "segment": "vip",
      "status": "active",
      "total_orders": 15,
      "total_spent": 150000,
      "last_order_at": "2026-02-18T10:30:00Z",
      "created_at": "2026-02-18T10:30:00Z",
      "tags": ["vip", "repeat_customer"]
    }
  ],
  "pagination": { ... }
}
```

#### POST /api/v1/customers
创建客户。

#### GET /api/v1/customers/{customer_id}
获取客户详情。

#### PUT /api/v1/customers/{customer_id}
更新客户信息。

#### GET /api/v1/customers/{customer_id}/orders
获取客户订单历史。

#### GET /api/v1/customers/{customer_id}/statistics
获取客户统计。

### 8.2 客户分组
#### GET /api/v1/customer-segments
获取客户分组列表。

#### POST /api/v1/customer-segments
创建客户分组。

**请求体**：
```json
{
  "name": "VIP客户",
  "description": "累计消费超过10000元的客户",
  "rules": [
    {
      "field": "total_spent",
      "operator": "gte",
      "value": 10000
    }
  ],
  "auto_update": true
}
```

#### PUT /api/v1/customer-segments/{segment_id}
更新客户分组。

#### DELETE /api/v1/customer-segments/{segment_id}
删除客户分组。

#### POST /api/v1/customer-segments/{segment_id}/sync
手动同步分组客户。

### 8.3 营销活动
#### GET /api/v1/campaigns
获取营销活动列表。

#### POST /api/v1/campaigns
创建营销活动。

**请求体**：
```json
{
  "name": "春节促销",
  "segment_id": "segment_123",
  "template_id": "template_456",
  "type": "email",
  "scheduled_at": "2026-02-20T10:00:00Z",
  "content": {
    "subject": "春节特惠，全场8折",
    "body": "亲爱的客户，春节快乐..."
  }
}
```

#### POST /api/v1/campaigns/{campaign_id}/send
发送营销活动。

#### GET /api/v1/campaigns/{campaign_id}/statistics
获取营销活动统计。

## 9. AI Agent 服务 API

### 9.1 Agent 任务执行
#### POST /api/v1/agent/execute
执行Agent指令。

**请求体**：
```json
{
  "instruction": "检查所有店铺的滞销商品并给出处理建议",
  "parameters": {
    "days_threshold": 30,
    "include_suggestions": true
  },
  "async": true
}
```

**响应体**（同步模式）：
```json
{
  "task_id": "agent_task_123",
  "status": "completed",
  "result": {
    "total_products": 150,
    "slow_moving": 25,
    "suggestions": [
      {
        "product_id": "product_123",
        "sku": "SKU001",
        "suggestion": "降价促销",
        "reason": "30天内无销售"
      }
    ]
  },
  "execution_time": 15.2
}
```

**响应体**（异步模式）：
```json
{
  "task_id": "agent_task_123",
  "status": "queued",
  "message": "任务已加入队列"
}
```

#### GET /api/v1/agent/tasks/{task_id}
获取Agent任务状态和结果。

#### GET /api/v1/agent/tasks
获取Agent任务列表。

### 9.2 工作流管理
#### GET /api/v1/agent/workflows
获取工作流列表。

#### POST /api/v1/agent/workflows
创建工作流。

**请求体**：
```json
{
  "name": "自动处理滞销商品",
  "description": "自动识别滞销商品并执行降价促销",
  "trigger": {
    "type": "schedule",
    "schedule": "0 2 * * *" // 每天凌晨2点
  },
  "steps": [
    {
      "type": "find_slow_moving_products",
      "parameters": {"days_threshold": 30}
    },
    {
      "type": "apply_discount",
      "parameters": {"discount_percent": 20}
    },
    {
      "type": "send_notification",
      "parameters": {"channel": "email"}
    }
  ],
  "enabled": true
}
```

#### PUT /api/v1/agent/workflows/{workflow_id}
更新工作流。

#### DELETE /api/v1/agent/workflows/{workflow_id}
删除工作流。

#### POST /api/v1/agent/workflows/{workflow_id}/execute
手动执行工作流。

#### GET /api/v1/agent/workflows/{workflow_id}/executions
获取工作流执行历史。

### 9.3 Agent 工具管理
#### GET /api/v1/agent/tools
获取可用工具列表。

#### POST /api/v1/agent/tools
注册新工具。

**请求体**：
```json
{
  "name": "get_product_sales",
  "description": "获取商品销售数据",
  "endpoint": "/api/v1/products/{product_id}/sales",
  "parameters": [
    {
      "name": "product_id",
      "type": "string",
      "required": true,
      "description": "商品ID"
    },
    {
      "name": "period",
      "type": "string",
      "required": false,
      "default": "last_30_days",
      "description": "统计周期"
    }
  ],
  "returns": {
    "type": "object",
    "description": "销售数据"
  }
}
```

## 10. 通知服务 API

### 10.1 通知管理
#### GET /api/v1/notifications
获取通知列表。

**查询参数**：
- `type`：通知类型（system, order, inventory, customer, marketing）
- `read`：是否已读
- `important`：是否重要

**响应体**：
```json
{
  "items": [
    {
      "id": "notification_123",
      "type": "inventory",
      "title": "库存预警",
      "content": "商品SKU001库存低于安全库存",
      "important": true,
      "read": false,
      "data": {
        "product_id": "product_123",
        "sku": "SKU001",
        "current_stock": 15,
        "safety_stock": 20
      },
      "created_at": "2026-02-18T10:30:00Z"
    }
  ],
  "unread_count": 5
}
```

#### PUT /api/v1/notifications/{notification_id}/read
标记通知为已读。

#### PUT /api/v1/notifications/read-all
标记所有通知为已读。

#### GET /api/v1/notifications/settings
获取通知设置。

#### PUT /api/v1/notifications/settings
更新通知设置。

**请求体**：
```json
{
  "email": {
    "order_updates": true,
    "inventory_alerts": true,
    "marketing": false
  },
  "push": {
    "important_only": true
  },
  "sms": {
    "order_shipped": true,
    "payment_reminders": false
  }
}
```

## 11. 数据分析 API

### 11.1 仪表板数据
#### GET /api/v1/analytics/dashboard
获取仪表板数据。

**查询参数**：
- `period`：统计周期（today, yesterday, last_7_days, last_30_days, this_month, last_month）

**响应体**：
```json
{
  "summary": {
    "total_revenue": 1250000,
    "total_orders": 150,
    "total_customers": 100,
    "total_products": 500,
    "conversion_rate": 2.5,
    "average_order_value": 8333
  },
  "revenue_trend": [
    {"date": "2026-02-11", "revenue": 150000},
    {"date": "2026-02-12", "revenue": 180000}
  ],
  "top_products": [
    {"product_id": "product_123", "name": "无线蓝牙耳机", "sales": 50, "revenue": 100000},
    {"product_id": "product_456", "name": "智能手表", "sales": 30, "revenue": 75000}
  ],
  "platform_distribution": {
    "amazon": {"orders": 80, "revenue": 800000},
    "ozon": {"orders": 40, "revenue": 300000},
    "shopify": {"orders": 30, "revenue": 150000}
  }
}
```

### 11.2 销售分析
#### GET /api/v1/analytics/sales
获取销售分析数据。

**查询参数**：
- `start_date`, `end_date`：日期范围
- `group_by`：分组维度（day, week, month, product, platform, customer_segment）
- `shop_id`：按店铺筛选

**响应体**：
```json
{
  "period": {"start": "2026-02-11", "end": "2026-02-18"},
  "metrics": {
    "total_revenue": 1250000,
    "total_orders": 150,
    "average_order_value": 8333,
    "growth_rate": 15.5
  },
  "data": [
    {
      "group": "2026-02-11",
      "revenue": 150000,
      "orders": 18,
      "customers": 15
    }
  ]
}
```

### 11.3 库存分析
#### GET /api/v1/analytics/inventory
获取库存分析数据。

**响应体**：
```json
{
  "summary": {
    "total_value": 2500000,
    "total_sku_count": 500,
    "out_of_stock_count": 30,
    "low_stock_count": 45,
    "excess_stock_count": 20
  },
  "turnover_rate": 2.5,
  "aging_analysis": {
    "0_30_days": {"count": 300, "value": 1500000},
    "31_60_days": {"count": 120, "value": 600000},
    "61_90_days": {"count": 50, "value": 250000},
    "90_plus_days": {"count": 30, "value": 150000}
  },
  "abc_analysis": {
    "A": {"count": 50, "value": 1500000, "percentage": 60},
    "B": {"count": 150, "value": 750000, "percentage": 30},
    "C": {"count": 300, "value": 250000, "percentage": 10}
  }
}
```

## 12. 文件上传 API

### 12.1 文件上传
#### POST /api/v1/upload
上传文件。

**Content-Type**: `multipart/form-data`

**表单字段**：
- `file`: 文件内容
- `type`: 文件类型（product_image, product_video, document, import_file）
- `reference_id`: 关联资源ID（可选）
- `reference_type`: 关联资源类型（product, order, customer等）

**响应体**：
```json
{
  "file_id": "file_123",
  "filename": "product_image.jpg",
  "url": "https://.../product_image.jpg",
  "size": 1024000,
  "mime_type": "image/jpeg",
  "uploaded_at": "2026-02-18T10:30:00Z"
}
```

#### DELETE /api/v1/upload/{file_id}
删除文件。

## 13. Webhook 配置

### 13.1 Webhook 管理
#### GET /api/v1/webhooks
获取Webhook列表。

#### POST /api/v1/webhooks
创建Webhook。

**请求体**：
```json
{
  "name": "订单创建通知",
  "url": "https://your-server.com/webhooks/order-created",
  "events": ["order.created", "order.paid", "order.shipped"],
  "secret": "your_secret_key",
  "enabled": true
}
```

#### PUT /api/v1/webhooks/{webhook_id}
更新Webhook。

#### DELETE /api/v1/webhooks/{webhook_id}
删除Webhook。

#### POST /api/v1/webhooks/{webhook_id}/test
测试Webhook。

### 13.2 Webhook 事件
系统支持以下Webhook事件：
- `order.created`: 订单创建
- `order.paid`: 订单支付
- `order.shipped`: 订单发货
- `order.completed`: 订单完成
- `order.cancelled`: 订单取消
- `inventory.low_stock`: 库存低于安全库存
- `inventory.out_of_stock`: 库存缺货
- `product.created`: 商品创建
- `product.updated`: 商品更新
- `customer.created`: 客户创建
- `customer.updated`: 客户更新

## 14. API 限流策略

### 14.1 限流规则
| API类别 | 限流规则 | 说明 |
|---------|----------|------|
| **认证API** | 100次/小时/IP | 防止暴力破解 |
| **公开API** | 1000次/小时/IP | 公开接口访问限制 |
| **用户API** | 5000次/小时/用户 | 普通用户API访问 |
| **管理API** | 10000次/小时/用户 | 管理员API访问 |
| **批量操作** | 100次/小时/用户 | 批量操作限制 |

### 14.2 限流响应头
- `X-RateLimit-Limit`: 限流上限
- `X-RateLimit-Remaining`: 剩余请求次数
- `X-RateLimit-Reset`: 限流重置时间（Unix时间戳）

## 15. API 版本管理

### 15.1 版本策略
- **URL路径版本**：`/api/v1/` 包含版本号
- **向后兼容**：新版本必须兼容旧版本的数据结构
- **弃用策略**：旧版本API至少维护6个月后才可弃用
- **版本迁移**：提供迁移指南和工具

### 15.2 当前版本
- **v1.0**：基础API版本，包含核心功能
- **计划版本**：
  - v2.0：增加高级AI功能，优化数据结构
  - v3.0：增加开放平台API，第三方集成

## 16. API 测试

### 16.1 测试环境
- **测试地址**：`https://api-test.icross.com/api/v1/`
- **测试账号**：
  - 普通用户：`test@icross.com` / `Test123456`
  - 管理员：`admin@icross.com` / `Admin123456`

### 16.2 测试工具
- **Postman**：API测试集合
- **Swagger UI**：`/docs` 接口文档和测试
- **API自动化测试**：集成到CI/CD流程

## 附录

### A. 数据格式规范

#### 日期时间
- ISO 8601格式：`YYYY-MM-DDTHH:mm:ssZ`
- 时区：UTC时间，前端根据用户时区转换

#### 金额
- 整数存储，单位为分
- 显示时除以100转为元/美元等
- 货币代码：ISO 4217标准（CNY, USD, EUR等）

#### 分页响应
```json
{
  "items": [...],
  "pagination": {
    "total": 1000,
    "page": 1,
    "limit": 20,
    "pages": 50,
    "has_next": true,
    "has_prev": false
  }
}
```

### B. 快速开始示例

#### 1. 获取访问令牌
```bash
curl -X POST https://api.icross.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

#### 2. 获取商品列表
```bash
curl -X GET https://api.icross.com/api/v1/products \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### 3. 创建订单
```bash
curl -X POST https://api.icross.com/api/v1/orders \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": "shop_789",
    "customer_id": "customer_123",
    "items": [
      {
        "product_id": "product_456",
        "quantity": 2
      }
    ]
  }'
```

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v2.0 | 2026-02-18 | 全面API设计，覆盖所有核心服务 | AI Assistant |
| v1.0 | 2026-02-14 | 初始API设计草案 | 架构团队 |

*本文档将随着API演进持续更新。*
