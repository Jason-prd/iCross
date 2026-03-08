# iCross 数据库设计文档

## 文档信息

| 项目 | 说明 |
|------|------|
| **文档版本** | v2.0 |
| **最后更新** | 2026-02-18 |
| **数据库版本** | PostgreSQL 15+ |
| **设计原则** | 规范设计，适当反范式优化 |
| **文档负责人** | 数据库架构师 |

## 1. 数据库设计原则

### 1.1 设计规范
- **命名规范**：
  - 表名：小写，下划线分隔，复数形式（`users`, `orders`）
  - 字段名：小写，下划线分隔（`created_at`, `updated_at`）
  - 主键：`id`（UUID v7 或自增序列）
  - 外键：`{table_name}_id`（`user_id`, `order_id`）
  - 索引：`idx_{table}_{columns}`，唯一索引 `unq_{table}_{columns}`
- **数据类型**：
  - 标识符：UUID（`gen_random_uuid()`）
  - 时间戳：`timestamptz`（带时区时间戳）
  - 金额：`bigint`（单位：分）
  - 状态：`smallint` 或 `varchar(20)`
  - JSON数据：`jsonb`（支持索引和查询）
- **约束**：
  - 非空约束：`NOT NULL` 对必填字段
  - 唯一约束：`UNIQUE` 对唯一性字段
  - 外键约束：`FOREIGN KEY` 关联完整性
  - 检查约束：`CHECK` 数据有效性

### 1.2 多租户设计
- **方案选择**：Schema隔离 + 租户ID字段
- **数据隔离**：每个租户独立Schema，确保数据安全
- **公共表**：系统级表在公共Schema（`users`, `tenants`）
- **租户表**：业务表在各租户Schema中
- **连接管理**：连接池根据租户动态切换Schema

### 1.3 性能优化
- **索引策略**：常用查询字段创建索引，避免过度索引
- **分区策略**：大表按时间分区（订单表按月分区）
- **查询优化**：避免N+1查询，使用JOIN和预加载
- **缓存策略**：热点数据Redis缓存，减少数据库压力

## 2. 核心表结构

### 2.1 系统与用户表

#### tenants (租户表)
存储租户（团队）信息。

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, suspended, deleted
    settings JSONB NOT NULL DEFAULT '{}',
    billing_email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 索引
    INDEX idx_tenants_subdomain (subdomain),
    INDEX idx_tenants_status (status),
    INDEX idx_tenants_created_at (created_at)
);
```

#### users (用户表)
系统用户表，存储所有用户信息。

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    avatar_url TEXT,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- super_admin, admin, manager, member, viewer
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, inactive, suspended
    last_login_at TIMESTAMPTZ,
    login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    UNIQUE (tenant_id, email),
    
    -- 索引
    INDEX idx_users_tenant_id (tenant_id),
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
);
```

#### user_sessions (用户会话表)
存储用户登录会话信息。

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_user_sessions_user_id (user_id),
    INDEX idx_user_sessions_token_hash (token_hash),
    INDEX idx_user_sessions_expires_at (expires_at)
);
```

#### audit_logs (审计日志表)
记录所有关键操作日志。

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- create, update, delete, login, logout
    resource_type VARCHAR(100) NOT NULL, -- user, product, order, etc.
    resource_id VARCHAR(100),
    changes JSONB, -- 变更前后的数据
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(20) NOT NULL, -- success, failure
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_audit_logs_tenant_id (tenant_id),
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_resource_type (resource_type),
    INDEX idx_audit_logs_created_at (created_at)
);
```

### 2.2 店铺与平台表

#### shops (店铺表)
存储连接的电商平台店铺信息。

```sql
CREATE TABLE shops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- amazon, ozon, shopify, ebay, aliexpress
    platform_shop_id VARCHAR(255) NOT NULL, -- 平台店铺ID
    country_code VARCHAR(2) NOT NULL, -- 店铺所在国家
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    
    -- API配置
    api_key VARCHAR(500),
    api_secret VARCHAR(500),
    api_token TEXT,
    api_token_expires_at TIMESTAMPTZ,
    
    -- 同步配置
    sync_settings JSONB NOT NULL DEFAULT '{
        "auto_sync": true,
        "sync_interval": 300,
        "sync_products": true,
        "sync_orders": true,
        "sync_inventory": true,
        "sync_customers": true
    }',
    
    -- 状态信息
    status VARCHAR(20) NOT NULL DEFAULT 'disconnected', -- connected, disconnected, error
    last_sync_at TIMESTAMPTZ,
    last_sync_status VARCHAR(20), -- success, partial_failure, failure
    error_message TEXT,
    sync_statistics JSONB NOT NULL DEFAULT '{}',
    
    -- 元数据
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, platform, platform_shop_id),
    
    -- 索引
    INDEX idx_shops_tenant_id (tenant_id),
    INDEX idx_shops_platform (platform),
    INDEX idx_shops_status (status),
    INDEX idx_shops_last_sync_at (last_sync_at)
);
```

#### shop_sync_logs (店铺同步日志表)
记录店铺同步历史。

```sql
CREATE TABLE shop_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL, -- full, incremental, products, orders, inventory
    status VARCHAR(20) NOT NULL, -- pending, running, success, failed
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    statistics JSONB NOT NULL DEFAULT '{}', -- 同步统计
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_shop_sync_logs_shop_id (shop_id),
    INDEX idx_shop_sync_logs_status (status),
    INDEX idx_shop_sync_logs_started_at (started_at),
    INDEX idx_shop_sync_logs_sync_type (sync_type)
);
```

### 2.3 商品与分类表

#### categories (分类表)
商品分类，支持多级分类。

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    platform_category_id VARCHAR(255), -- 平台分类ID
    platform VARCHAR(50), -- 所属平台
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, slug),
    UNIQUE (tenant_id, platform, platform_category_id) WHERE platform IS NOT NULL AND platform_category_id IS NOT NULL,
    
    -- 索引
    INDEX idx_categories_tenant_id (tenant_id),
    INDEX idx_categories_parent_id (parent_id),
    INDEX idx_categories_slug (slug),
    INDEX idx_categories_is_active (is_active)
);
```

#### products (商品表)
核心商品表，存储商品基本信息。

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    platform_product_id VARCHAR(255) NOT NULL, -- 平台商品ID
    sku VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    short_description TEXT,
    
    -- 价格信息
    price BIGINT NOT NULL, -- 单位：分
    original_price BIGINT,
    cost_price BIGINT, -- 成本价
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    
    -- 分类与属性
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    brand VARCHAR(255),
    attributes JSONB NOT NULL DEFAULT '{}', -- 商品属性
    specifications JSONB NOT NULL DEFAULT '{}', -- 规格参数
    
    -- 状态与库存
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- draft, active, inactive, archived
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    min_stock_quantity INTEGER NOT NULL DEFAULT 0,
    
    -- 图片与多媒体
    main_image_url TEXT,
    image_urls TEXT[] NOT NULL DEFAULT '{}',
    video_urls TEXT[] NOT NULL DEFAULT '{}',
    
    -- SEO信息
    seo_title VARCHAR(255),
    seo_description TEXT,
    seo_keywords TEXT[] NOT NULL DEFAULT '{}',
    
    -- 统计信息
    view_count INTEGER NOT NULL DEFAULT 0,
    sale_count INTEGER NOT NULL DEFAULT 0,
    rating DECIMAL(3,2) NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    
    -- 同步信息
    last_synced_at TIMESTAMPTZ,
    sync_status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, synced, error
    platform_data JSONB NOT NULL DEFAULT '{}', -- 平台原始数据
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    
    -- 约束
    UNIQUE (shop_id, platform_product_id),
    UNIQUE (tenant_id, sku), -- 租户内SKU唯一
    
    -- 索引
    INDEX idx_products_tenant_id (tenant_id),
    INDEX idx_products_shop_id (shop_id),
    INDEX idx_products_sku (sku),
    INDEX idx_products_status (status),
    INDEX idx_products_category_id (category_id),
    INDEX idx_products_price (price),
    INDEX idx_products_created_at (created_at)
) PARTITION BY RANGE (created_at); -- 按创建时间分区
```

#### product_variants (商品变体表)
商品变体信息，如颜色、尺寸等。

```sql
CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL,
    variant_sku VARCHAR(100), -- 变体SKU（如SKU-BLACK-M）
    platform_variant_id VARCHAR(255), -- 平台变体ID
    
    -- 变体属性
    attributes JSONB NOT NULL DEFAULT '{}', -- {"color": "black", "size": "M"}
    
    -- 价格与库存
    price BIGINT, -- 变体价格，为空则使用商品价格
    cost_price BIGINT,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    
    -- 图片
    image_url TEXT,
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (product_id, sku),
    UNIQUE (product_id, platform_variant_id) WHERE platform_variant_id IS NOT NULL,
    
    -- 索引
    INDEX idx_product_variants_product_id (product_id),
    INDEX idx_product_variants_sku (sku),
    INDEX idx_product_variants_status (status)
);
```

#### product_prices (商品价格历史表)
记录商品价格变更历史。

```sql
CREATE TABLE product_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(id) ON DELETE CASCADE,
    price_type VARCHAR(50) NOT NULL, -- sale, regular, cost, suggested
    price BIGINT NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMPTZ,
    reason VARCHAR(100), -- manual, auto, promotion, competition
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_product_prices_product_id (product_id),
    INDEX idx_product_prices_variant_id (variant_id),
    INDEX idx_product_prices_effective_from (effective_from),
    INDEX idx_product_prices_price_type (price_type)
);
```

### 2.4 库存与仓库表

#### warehouses (仓库表)
物理或虚拟仓库信息。

```sql
CREATE TABLE warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL, -- 仓库代码（如WH001）
    type VARCHAR(50) NOT NULL DEFAULT 'physical', -- physical, virtual, dropship
    contact_person VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    
    -- 地址信息
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country_code VARCHAR(2),
    postal_code VARCHAR(20),
    
    -- 运营信息
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    capacity INTEGER, -- 容量（SKU数量）
    current_usage INTEGER NOT NULL DEFAULT 0,
    operating_hours JSONB,
    
    -- 物流信息
    shipping_zones JSONB NOT NULL DEFAULT '[]', -- 服务区域
    shipping_methods JSONB NOT NULL DEFAULT '[]', -- 支持的物流方式
    
    -- 元数据
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, code),
    
    -- 索引
    INDEX idx_warehouses_tenant_id (tenant_id),
    INDEX idx_warehouses_type (type),
    INDEX idx_warehouses_is_active (is_active)
);
```

#### inventory (库存表)
商品库存记录，支持多仓库。

```sql
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES product_variants(id) ON DELETE CASCADE,
    warehouse_id UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    
    -- 库存数量
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    
    -- 库存配置
    min_quantity INTEGER NOT NULL DEFAULT 0, -- 最小库存
    max_quantity INTEGER, -- 最大库存
    reorder_point INTEGER, -- 补货点
    safety_stock INTEGER NOT NULL DEFAULT 0, -- 安全库存
    
    -- 批次信息（针对有保质期商品）
    batch_number VARCHAR(100),
    manufacture_date DATE,
    expiry_date DATE,
    
    -- 位置信息
    location_code VARCHAR(100), -- 库位代码（如A-01-02）
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'normal', -- normal, low_stock, out_of_stock, excess_stock
    last_counted_at TIMESTAMPTZ, -- 上次盘点时间
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (product_id, variant_id, warehouse_id),
    CHECK (quantity >= 0),
    CHECK (reserved_quantity >= 0),
    CHECK (reserved_quantity <= quantity),
    
    -- 索引
    INDEX idx_inventory_tenant_id (tenant_id),
    INDEX idx_inventory_product_id (product_id),
    INDEX idx_inventory_variant_id (variant_id),
    INDEX idx_inventory_warehouse_id (warehouse_id),
    INDEX idx_inventory_status (status),
    INDEX idx_inventory_available_quantity (available_quantity)
);
```

#### inventory_transactions (库存事务表)
记录所有库存变更。

```sql
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    inventory_id UUID NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    
    -- 事务信息
    transaction_type VARCHAR(50) NOT NULL, -- purchase, sale, adjustment, transfer, return
    reference_type VARCHAR(50), -- order, purchase_order, adjustment, transfer
    reference_id VARCHAR(100),
    
    -- 数量变化
    quantity_change INTEGER NOT NULL, -- 正数增加，负数减少
    quantity_before INTEGER NOT NULL,
    quantity_after INTEGER NOT NULL,
    
    -- 成本信息
    unit_cost BIGINT, -- 单位成本（分）
    total_cost BIGINT, -- 总成本
    
    -- 事务详情
    reason VARCHAR(100),
    notes TEXT,
    performed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_inventory_transactions_tenant_id (tenant_id),
    INDEX idx_inventory_transactions_inventory_id (inventory_id),
    INDEX idx_inventory_transactions_transaction_type (transaction_type),
    INDEX idx_inventory_transactions_reference_type (reference_type, reference_id),
    INDEX idx_inventory_transactions_created_at (created_at)
);
```

#### inventory_alerts (库存预警表)
库存预警记录。

```sql
CREATE TABLE inventory_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    inventory_id UUID NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    
    -- 预警信息
    alert_type VARCHAR(50) NOT NULL, -- low_stock, out_of_stock, excess_stock, expiry
    severity VARCHAR(20) NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    current_quantity INTEGER NOT NULL,
    threshold_quantity INTEGER NOT NULL,
    
    -- 处理状态
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, acknowledged, resolved
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    -- 通知状态
    notified BOOLEAN NOT NULL DEFAULT FALSE,
    last_notified_at TIMESTAMPTZ,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_inventory_alerts_tenant_id (tenant_id),
    INDEX idx_inventory_alerts_inventory_id (inventory_id),
    INDEX idx_inventory_alerts_alert_type (alert_type),
    INDEX idx_inventory_alerts_status (status),
    INDEX idx_inventory_alerts_created_at (created_at)
);
```

### 2.5 订单与客户表

#### customers (客户表)
B端和C端客户信息。

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 基本信息
    customer_type VARCHAR(20) NOT NULL DEFAULT 'b2c', -- b2c, b2b
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    tax_id VARCHAR(100), -- 税号
    
    -- 地址信息
    billing_address JSONB,
    shipping_address JSONB,
    
    -- 客户分组
    segment_id UUID REFERENCES customer_segments(id) ON DELETE SET NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    
    -- 统计信息
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_spent BIGINT NOT NULL DEFAULT 0, -- 单位：分
    first_order_at TIMESTAMPTZ,
    last_order_at TIMESTAMPTZ,
    
    -- 状态与评分
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, inactive, blocked
    customer_score INTEGER NOT NULL DEFAULT 0, -- 客户评分（0-100）
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low', -- low, medium, high
    
    -- 营销偏好
    marketing_preferences JSONB NOT NULL DEFAULT '{
        "email": true,
        "sms": false,
        "push": true
    }',
    
    -- 备注
    notes TEXT,
    
    -- 平台信息
    platform_customer_id VARCHAR(255), -- 平台客户ID
    platform VARCHAR(50),
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, email) WHERE email IS NOT NULL,
    UNIQUE (tenant_id, phone) WHERE phone IS NOT NULL,
    UNIQUE (tenant_id, platform, platform_customer_id) WHERE platform IS NOT NULL AND platform_customer_id IS NOT NULL,
    
    -- 索引
    INDEX idx_customers_tenant_id (tenant_id),
    INDEX idx_customers_email (email),
    INDEX idx_customers_phone (phone),
    INDEX idx_customers_customer_type (customer_type),
    INDEX idx_customers_status (status),
    INDEX idx_customers_total_spent (total_spent),
    INDEX idx_customers_created_at (created_at)
);
```

#### customer_segments (客户分组表)
客户分组定义。

```sql
CREATE TABLE customer_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- 分组规则
    rules JSONB NOT NULL DEFAULT '[]', -- 分组规则定义
    is_dynamic BOOLEAN NOT NULL DEFAULT TRUE, -- 是否动态分组
    auto_update BOOLEAN NOT NULL DEFAULT TRUE, -- 是否自动更新
    
    -- 统计信息
    customer_count INTEGER NOT NULL DEFAULT 0,
    total_spent BIGINT NOT NULL DEFAULT 0,
    avg_order_value BIGINT NOT NULL DEFAULT 0,
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name),
    
    -- 索引
    INDEX idx_customer_segments_tenant_id (tenant_id),
    INDEX idx_customer_segments_is_active (is_active)
);
```

#### orders (订单表)
客户订单信息。

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    
    -- 订单标识
    order_number VARCHAR(100) NOT NULL, -- 系统订单号（如ORD-20260218-001）
    platform_order_id VARCHAR(255) NOT NULL, -- 平台订单ID
    platform VARCHAR(50) NOT NULL, -- 订单来源平台
    
    -- 订单状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, paid, processing, shipped, delivered, completed, cancelled, refunded
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, paid, partially_paid, refunded
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'unfulfilled', -- unfulfilled, partially_fulfilled, fulfilled
    
    -- 金额信息
    subtotal_amount BIGINT NOT NULL DEFAULT 0, -- 商品小计
    shipping_amount BIGINT NOT NULL DEFAULT 0, -- 运费
    tax_amount BIGINT NOT NULL DEFAULT 0, -- 税费
    discount_amount BIGINT NOT NULL DEFAULT 0, -- 折扣
    total_amount BIGINT NOT NULL DEFAULT 0, -- 订单总额
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    
    -- 支付信息
    payment_method VARCHAR(100),
    payment_gateway VARCHAR(100),
    transaction_id VARCHAR(255),
    paid_at TIMESTAMPTZ,
    
    -- 物流信息
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),
    shipped_at TIMESTAMPTZ,
    estimated_delivery_date DATE,
    delivered_at TIMESTAMPTZ,
    
    -- 地址信息
    billing_address JSONB NOT NULL,
    shipping_address JSONB NOT NULL,
    
    -- 客户备注
    customer_note TEXT,
    internal_note TEXT,
    
    -- 取消/退款信息
    cancelled_at TIMESTAMPTZ,
    cancelled_reason VARCHAR(100),
    refunded_amount BIGINT NOT NULL DEFAULT 0,
    refunded_at TIMESTAMPTZ,
    
    -- 平台数据
    platform_data JSONB NOT NULL DEFAULT '{}', -- 平台原始数据
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, order_number),
    UNIQUE (shop_id, platform_order_id),
    CHECK (total_amount >= 0),
    
    -- 索引
    INDEX idx_orders_tenant_id (tenant_id),
    INDEX idx_orders_shop_id (shop_id),
    INDEX idx_orders_customer_id (customer_id),
    INDEX idx_orders_order_number (order_number),
    INDEX idx_orders_status (status),
    INDEX idx_orders_payment_status (payment_status),
    INDEX idx_orders_created_at (created_at),
    INDEX idx_orders_total_amount (total_amount)
) PARTITION BY RANGE (created_at); -- 按创建时间分区
```

#### order_items (订单商品表)
订单商品明细。

```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    variant_id UUID REFERENCES product_variants(id) ON DELETE RESTRICT,
    
    -- 商品信息
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}', -- 商品属性
    
    -- 价格与数量
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL, -- 单价（分）
    original_unit_price BIGINT, -- 原价
    subtotal_amount BIGINT NOT NULL, -- 小计（quantity * unit_price）
    
    -- 折扣
    discount_amount BIGINT NOT NULL DEFAULT 0,
    
    -- 成本信息
    unit_cost BIGINT, -- 单位成本
    total_cost BIGINT, -- 总成本（quantity * unit_cost）
    
    -- 物流信息
    shipping_amount BIGINT NOT NULL DEFAULT 0,
    tax_amount BIGINT NOT NULL DEFAULT 0,
    
    -- 状态
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'unfulfilled', -- unfulfilled, partially_fulfilled, fulfilled
    shipped_quantity INTEGER NOT NULL DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_order_items_tenant_id (tenant_id),
    INDEX idx_order_items_order_id (order_id),
    INDEX idx_order_items_product_id (product_id),
    INDEX idx_order_items_variant_id (variant_id),
    INDEX idx_order_items_sku (sku)
);
```

#### order_fulfillments (订单履约表)
订单发货履约记录。

```sql
CREATE TABLE order_fulfillments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    -- 履约信息
    fulfillment_type VARCHAR(50) NOT NULL DEFAULT 'shipment', -- shipment, pickup, digital
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, shipped, delivered, cancelled
    
    -- 物流信息
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),
    carrier_service VARCHAR(100),
    tracking_url TEXT,
    
    -- 包裹信息
    package_weight DECIMAL(10,2), -- 重量（kg）
    package_dimensions JSONB, -- 尺寸 {"length": 30, "width": 20, "height": 10, "unit": "cm"}
    
    -- 时间信息
    shipped_at TIMESTAMPTZ,
    estimated_delivery_date DATE,
    delivered_at TIMESTAMPTZ,
    
    -- 操作信息
    fulfilled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_order_fulfillments_tenant_id (tenant_id),
    INDEX idx_order_fulfillments_order_id (order_id),
    INDEX idx_order_fulfillments_status (status),
    INDEX idx_order_fulfillments_tracking_number (tracking_number),
    INDEX idx_order_fulfillments_shipped_at (shipped_at)
);
```

#### fulfillment_items (履约商品表)
履约包含的商品。

```sql
CREATE TABLE fulfillment_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fulfillment_id UUID NOT NULL REFERENCES order_fulfillments(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (fulfillment_id, order_item_id),
    
    -- 索引
    INDEX idx_fulfillment_items_fulfillment_id (fulfillment_id),
    INDEX idx_fulfillment_items_order_item_id (order_item_id)
);
```

### 2.6 采购与供应商表

#### suppliers (供应商表)
商品供应商信息。

```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 基本信息
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL, -- 供应商代码（如SUP001）
    type VARCHAR(50) NOT NULL DEFAULT 'manufacturer', -- manufacturer, distributor, wholesaler, dropshipper
    contact_person VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- 地址信息
    address JSONB NOT NULL DEFAULT '{}',
    
    -- 财务信息
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY',
    payment_terms VARCHAR(100), -- 付款条件（如Net 30）
    tax_id VARCHAR(100),
    
    -- 评级与状态
    rating DECIMAL(3,2) NOT NULL DEFAULT 0, -- 供应商评分（0-5）
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, inactive, suspended
    is_preferred BOOLEAN NOT NULL DEFAULT FALSE, -- 是否优选供应商
    
    -- 统计信息
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_amount BIGINT NOT NULL DEFAULT 0,
    average_delivery_time INTEGER, -- 平均交货时间（天）
    
    -- 备注
    notes TEXT,
    
    -- 平台信息（如1688供应商）
    platform_supplier_id VARCHAR(255),
    platform VARCHAR(50),
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, code),
    UNIQUE (tenant_id, platform, platform_supplier_id) WHERE platform IS NOT NULL AND platform_supplier_id IS NOT NULL,
    
    -- 索引
    INDEX idx_suppliers_tenant_id (tenant_id),
    INDEX idx_suppliers_name (name),
    INDEX idx_suppliers_type (type),
    INDEX idx_suppliers_status (status),
    INDEX idx_suppliers_rating (rating)
);
```

#### purchase_orders (采购订单表)
向供应商的采购订单。

```sql
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    
    -- 订单标识
    po_number VARCHAR(100) NOT NULL, -- 采购订单号（如PO-20260218-001）
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'draft', -- draft, pending_approval, approved, ordered, partially_received, received, cancelled, closed
    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
    
    -- 金额信息
    subtotal_amount BIGINT NOT NULL DEFAULT 0,
    shipping_amount BIGINT NOT NULL DEFAULT 0,
    tax_amount BIGINT NOT NULL DEFAULT 0,
    total_amount BIGINT NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY',
    
    -- 交付信息
    expected_delivery_date DATE,
    delivery_address JSONB,
    
    -- 审批信息
    requested_by UUID REFERENCES users(id) ON DELETE SET NULL,
    requested_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    
    -- 订单信息
    ordered_at TIMESTAMPTZ,
    order_reference VARCHAR(255), -- 供应商订单号
    
    -- 收货信息
    received_at TIMESTAMPTZ,
    received_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 备注
    notes TEXT,
    terms_and_conditions TEXT,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, po_number),
    CHECK (total_amount >= 0),
    
    -- 索引
    INDEX idx_purchase_orders_tenant_id (tenant_id),
    INDEX idx_purchase_orders_supplier_id (supplier_id),
    INDEX idx_purchase_orders_po_number (po_number),
    INDEX idx_purchase_orders_status (status),
    INDEX idx_purchase_orders_created_at (created_at)
);
```

#### purchase_order_items (采购订单商品表)
采购订单商品明细。

```sql
CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    
    -- 商品信息
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- 采购信息
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price BIGINT NOT NULL,
    subtotal_amount BIGINT NOT NULL,
    
    -- 收货信息
    received_quantity INTEGER NOT NULL DEFAULT 0,
    rejected_quantity INTEGER NOT NULL DEFAULT 0,
    
    -- 质量信息
    quality_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, accepted, rejected
    quality_notes TEXT,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_purchase_order_items_tenant_id (tenant_id),
    INDEX idx_purchase_order_items_purchase_order_id (purchase_order_id),
    INDEX idx_purchase_order_items_product_id (product_id),
    INDEX idx_purchase_order_items_sku (sku)
);
```

### 2.7 AI与AIGC相关表

#### aigc_tasks (AIGC任务表)
AIGC内容生成任务记录。

```sql
CREATE TABLE aigc_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 任务信息
    task_type VARCHAR(50) NOT NULL, -- text_generation, image_generation, video_generation, translation
    content_type VARCHAR(50) NOT NULL, -- product_title, product_description, product_image, marketing_video
    model_name VARCHAR(100) NOT NULL, -- 使用的模型（如gpt-4, dalle-3, stable-diffusion）
    
    -- 输入与输出
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB,
    parameters JSONB NOT NULL DEFAULT '{}', -- 生成参数
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    progress INTEGER NOT NULL DEFAULT 0, -- 进度百分比（0-100）
    
    -- 结果信息
    result_url TEXT, -- 生成内容URL（如图片、视频）
    result_text TEXT, -- 生成文本
    error_message TEXT,
    
    -- 成本信息
    tokens_used INTEGER,
    cost DECIMAL(10,4), -- 成本（美元）
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_aigc_tasks_tenant_id (tenant_id),
    INDEX idx_aigc_tasks_user_id (user_id),
    INDEX idx_aigc_tasks_task_type (task_type),
    INDEX idx_aigc_tasks_status (status),
    INDEX idx_aigc_tasks_created_at (created_at)
);
```

#### aigc_templates (AIGC模板表)
AIGC生成模板。

```sql
CREATE TABLE aigc_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 模板信息
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- product_title, product_description, seo_keywords, image_prompt
    category VARCHAR(100),
    
    -- 模板内容
    template_text TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '[]', -- 模板变量定义
    examples JSONB NOT NULL DEFAULT '[]', -- 示例
    
    -- 模型配置
    model_name VARCHAR(100),
    parameters JSONB NOT NULL DEFAULT '{}', -- 模型参数
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT FALSE, -- 是否系统模板
    
    -- 统计
    usage_count INTEGER NOT NULL DEFAULT 0,
    avg_rating DECIMAL(3,2) NOT NULL DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name),
    
    -- 索引
    INDEX idx_aigc_templates_tenant_id (tenant_id),
    INDEX idx_aigc_templates_template_type (template_type),
    INDEX idx_aigc_templates_is_active (is_active)
);
```

#### agent_tasks (AI Agent任务表)
AI Agent执行任务记录。

```sql
CREATE TABLE agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 任务信息
    task_type VARCHAR(100) NOT NULL, -- analysis, optimization, automation, report
    instruction TEXT NOT NULL, -- 用户指令
    agent_name VARCHAR(100) NOT NULL, -- 执行任务的Agent名称
    
    -- 状态与进度
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress INTEGER NOT NULL DEFAULT 0,
    current_step VARCHAR(100),
    
    -- 输入与输出
    input_data JSONB NOT NULL DEFAULT '{}',
    result_data JSONB,
    error_data JSONB,
    
    -- 执行信息
    tools_used JSONB NOT NULL DEFAULT '[]', -- 使用的工具列表
    steps_executed JSONB NOT NULL DEFAULT '[]', -- 执行步骤记录
    
    -- 性能指标
    tokens_used INTEGER,
    execution_time_ms INTEGER,
    cost DECIMAL(10,4),
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 索引
    INDEX idx_agent_tasks_tenant_id (tenant_id),
    INDEX idx_agent_tasks_user_id (user_id),
    INDEX idx_agent_tasks_task_type (task_type),
    INDEX idx_agent_tasks_status (status),
    INDEX idx_agent_tasks_created_at (created_at)
);
```

#### agent_workflows (AI Agent工作流表)
AI Agent工作流定义。

```sql
CREATE TABLE agent_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- 工作流信息
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    
    -- 工作流定义
    trigger_config JSONB NOT NULL DEFAULT '{}', -- 触发条件
    steps JSONB NOT NULL DEFAULT '[]', -- 步骤定义
    variables JSONB NOT NULL DEFAULT '{}', -- 工作流变量
    error_handling JSONB NOT NULL DEFAULT '{}', -- 错误处理
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_template BOOLEAN NOT NULL DEFAULT FALSE, -- 是否模板
    
    -- 执行统计
    execution_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    avg_execution_time_ms INTEGER,
    last_executed_at TIMESTAMPTZ,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name, version),
    
    -- 索引
    INDEX idx_agent_workflows_tenant_id (tenant_id),
    INDEX idx_agent_workflows_user_id (user_id),
    INDEX idx_agent_workflows_is_active (is_active)
);
```

#### agent_tools (AI Agent工具表)
AI Agent可用工具定义。

```sql
CREATE TABLE agent_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 工具信息
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL, -- data_query, operation, analysis, notification
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    
    -- 工具定义
    endpoint VARCHAR(500) NOT NULL, -- 工具调用端点
    method VARCHAR(10) NOT NULL DEFAULT 'POST', -- HTTP方法
    parameters_schema JSONB NOT NULL DEFAULT '{}', -- 参数Schema
    response_schema JSONB NOT NULL DEFAULT '{}', -- 响应Schema
    authentication_required BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- 权限控制
    required_permissions JSONB NOT NULL DEFAULT '[]', -- 所需权限
    rate_limit INTEGER, -- 调用频率限制（次/分钟）
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT FALSE, -- 是否系统工具
    
    -- 统计
    usage_count INTEGER NOT NULL DEFAULT 0,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 0, -- 成功率百分比
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name, version),
    
    -- 索引
    INDEX idx_agent_tools_tenant_id (tenant_id),
    INDEX idx_agent_tools_category (category),
    INDEX idx_agent_tools_is_active (is_active)
);
```

### 2.8 通知与消息表

#### notifications (通知表)
系统通知消息。

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 通知信息
    type VARCHAR(50) NOT NULL, -- system, order, inventory, customer, marketing
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'normal', -- low, normal, high, urgent
    category VARCHAR(100),
    
    -- 关联数据
    reference_type VARCHAR(100), -- 关联资源类型
    reference_id VARCHAR(100), -- 关联资源ID
    action_url TEXT, -- 操作链接
    
    -- 状态
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_important BOOLEAN NOT NULL DEFAULT FALSE,
    sent_via JSONB NOT NULL DEFAULT '[]', -- 发送渠道 [email, push, in_app]
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    
    -- 索引
    INDEX idx_notifications_tenant_id (tenant_id),
    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_type (type),
    INDEX idx_notifications_is_read (is_read),
    INDEX idx_notifications_created_at (created_at)
);
```

#### notification_templates (通知模板表)
通知消息模板。

```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 模板信息
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- email, sms, push, in_app
    category VARCHAR(100) NOT NULL, -- order_confirmation, shipping_notification, etc.
    language VARCHAR(10) NOT NULL DEFAULT 'zh-CN',
    
    -- 模板内容
    subject VARCHAR(500), -- 邮件主题
    content TEXT NOT NULL, -- 模板内容
    variables JSONB NOT NULL DEFAULT '[]', -- 模板变量
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT FALSE, -- 是否系统模板
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name, type, language),
    
    -- 索引
    INDEX idx_notification_templates_tenant_id (tenant_id),
    INDEX idx_notification_templates_type (type),
    INDEX idx_notification_templates_category (category),
    INDEX idx_notification_templates_is_active (is_active)
);
```

### 2.9 数据分析表

#### analytics_metrics (分析指标表)
业务分析指标定义。

```sql
CREATE TABLE analytics_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- 指标信息
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- sales, inventory, customer, financial
    unit VARCHAR(50), -- 单位（如USD, pieces, percent）
    calculation_sql TEXT, -- 计算SQL
    dimensions JSONB NOT NULL DEFAULT '[]', -- 维度定义
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    refresh_interval VARCHAR(20) NOT NULL DEFAULT 'daily', -- hourly, daily, weekly, monthly
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, name),
    
    -- 索引
    INDEX idx_analytics_metrics_tenant_id (tenant_id),
    INDEX idx_analytics_metrics_category (category),
    INDEX idx_analytics_metrics_is_active (is_active)
);
```

#### analytics_data (分析数据表)
分析指标数据。

```sql
CREATE TABLE analytics_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    metric_id UUID NOT NULL REFERENCES analytics_metrics(id) ON DELETE CASCADE,
    
    -- 数据信息
    date DATE NOT NULL,
    dimension_values JSONB NOT NULL DEFAULT '{}', -- 维度值
    value DECIMAL(20,4) NOT NULL,
    change_from_previous DECIMAL(10,2), -- 与前一期的变化百分比
    
    -- 时间戳
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 约束
    UNIQUE (tenant_id, metric_id, date, dimension_values),
    
    -- 索引
    INDEX idx_analytics_data_tenant_id (tenant_id),
    INDEX idx_analytics_data_metric_id (metric_id),
    INDEX idx_analytics_data_date (date)
) PARTITION BY RANGE (date); -- 按日期分区
```

## 3. 数据库分区策略

### 3.1 分区方案
```sql
-- 订单表按月分区
CREATE TABLE orders_y2026m02 PARTITION OF orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE orders_y2026m03 PARTITION OF orders
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- 商品表按月分区
CREATE TABLE products_y2026m02 PARTITION OF products
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- 分析数据表按日分区
CREATE TABLE analytics_data_y2026m02d01 PARTITION OF analytics_data
    FOR VALUES FROM ('2026-02-01') TO ('2026-02-02');
```

### 3.2 分区管理
- **自动创建分区**：每月初创建下个月的分区
- **数据归档**：超过12个月的数据归档到历史表
- **分区维护**：定期清理过期分区，优化索引

## 4. 数据库索引策略

### 4.1 常用查询索引
```sql
-- 用户相关查询
CREATE INDEX idx_users_email_tenant ON users(tenant_id, email);
CREATE INDEX idx_users_role_status ON users(tenant_id, role, status);

-- 商品相关查询
CREATE INDEX idx_products_shop_status ON products(shop_id, status);
CREATE INDEX idx_products_category_status ON products(category_id, status);
CREATE INDEX idx_products_price_range ON products(price) WHERE status = 'active';

-- 订单相关查询
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at DESC);
CREATE INDEX idx_orders_status_date ON orders(status, created_at DESC);
CREATE INDEX idx_orders_total_amount ON orders(total_amount DESC);

-- 库存相关查询
CREATE INDEX idx_inventory_product_warehouse ON inventory(product_id, warehouse_id);
CREATE INDEX idx_inventory_low_stock ON inventory(available_quantity) WHERE available_quantity < safety_stock;

-- 客户相关查询
CREATE INDEX idx_customers_total_spent ON customers(total_spent DESC);
CREATE INDEX idx_customers_last_order ON customers(last_order_at DESC) WHERE last_order_at IS NOT NULL;
```

### 4.2 复合索引优化
- **覆盖索引**：包含查询所需的所有字段
- **索引顺序**：等值条件字段在前，范围条件字段在后
- **索引大小**：避免过大索引，影响写入性能

## 5. 数据库维护计划

### 5.1 日常维护
```sql
-- 每日自动任务
-- 1. 更新统计信息
ANALYZE;

-- 2. 清理过期数据
DELETE FROM user_sessions WHERE expires_at < NOW() - INTERVAL '7 days';
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '180 days';

-- 3. 重建索引（低峰期）
REINDEX INDEX CONCURRENTLY idx_orders_created_at;

-- 4. 更新物化视图
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily_summary;
```

### 5.2 备份策略
- **全量备份**：每日凌晨2点进行全量备份
- **增量备份**：WAL日志连续归档
- **备份验证**：每日验证备份完整性
- **备份保留**：本地保留7天，云端保留30天

### 5.3 监控指标
- **性能指标**：QPS、TPS、平均响应时间、慢查询数量
- **容量指标**：数据库大小、表大小、索引大小、连接数
- **健康指标**：CPU使用率、内存使用率、磁盘IO、锁等待

## 6. 数据迁移与版本管理

### 6.1 迁移工具
- **Alembic**：数据库迁移框架
- **迁移脚本**：每次数据库变更创建迁移脚本
- **版本控制**：迁移脚本纳入Git版本控制

### 6.2 迁移流程
1. **开发环境**：开发人员创建迁移脚本
2. **测试环境**：自动化测试验证迁移
3. **预发环境**：模拟生产环境验证
4. **生产环境**：低峰期执行迁移，备份回滚方案

### 6.3 回滚方案
- **数据备份**：迁移前全量备份
- **迁移事务**：迁移操作在事务中执行
- **回滚脚本**：每个迁移都有对应的回滚脚本

## 7. 数据字典

### 7.1 状态码定义

#### 用户状态 (users.status)
- `active`：正常状态
- `inactive`：未激活
- `suspended`：已暂停
- `deleted`：已删除（软删除）

#### 商品状态 (products.status)
- `draft`：草稿
- `active`：在售
- `inactive`：下架
- `archived`：已归档
- `out_of_stock`：缺货

#### 订单状态 (orders.status)
- `pending`：待支付
- `paid`：已支付
- `processing`：处理中
- `shipped`：已发货
- `delivered`：已送达
- `completed`：已完成
- `cancelled`：已取消
- `refunded`：已退款

#### 库存状态 (inventory.status)
- `normal`：正常
- `low_stock`：低库存
- `out_of_stock`：缺货
- `excess_stock`：库存过多

### 7.2 枚举类型
```sql
-- 用户角色枚举
CREATE TYPE user_role AS ENUM (
    'super_admin',
    'admin', 
    'manager',
    'member',
    'viewer'
);

-- 订单状态枚举
CREATE TYPE order_status AS ENUM (
    'pending',
    'paid',
    'processing',
    'shipped',
    'delivered',
    'completed',
    'cancelled',
    'refunded'
);

-- 商品状态枚举
CREATE TYPE product_status AS ENUM (
    'draft',
    'active',
    'inactive',
    'archived',
    'out_of_stock'
);
```

## 8. 性能优化建议

### 8.1 查询优化
- **避免SELECT ***：只选择需要的字段
- **使用JOIN替代子查询**：提高查询性能
- **合理使用索引**：根据查询模式创建索引
- **批量操作**：使用批量插入/更新

### 8.2 连接管理
- **连接池**：使用PgBouncer连接池
- **连接复用**：减少连接建立开销
- **超时设置**：合理设置查询超时时间

### 8.3 缓存策略
- **查询缓存**：Redis缓存热点查询结果
- **对象缓存**：缓存常用业务对象
- **CDN缓存**：静态资源CDN缓存

## 附录

### A. 数据库配置参考
```ini
# postgresql.conf 关键配置
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB
max_connections = 200

# 性能优化
random_page_cost = 1.1
effective_io_concurrency = 200
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```

### B. 常用查询示例
```sql
-- 获取今日订单统计
SELECT 
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM orders 
WHERE DATE(created_at) = CURRENT_DATE
    AND tenant_id = :tenant_id;

-- 获取低库存商品
SELECT 
    p.sku,
    p.title,
    i.available_quantity,
    i.safety_stock,
    w.name as warehouse_name
FROM inventory i
JOIN products p ON i.product_id = p.id
JOIN warehouses w ON i.warehouse_id = w.id
WHERE i.tenant_id = :tenant_id
    AND i.available_quantity < i.safety_stock
    AND p.status = 'active'
ORDER BY i.available_quantity ASC;

-- 获取客户购买分析
SELECT 
    c.name,
    c.email,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent,
    MAX(o.created_at) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.tenant_id = :tenant_id
    AND c.status = 'active'
GROUP BY c.id
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 100;
```

### C. 数据库扩展方案
1. **读写分离**：主库写，从库读
2. **分库分表**：按租户分库，按时间分表
3. **数据归档**：历史数据归档到冷存储
4. **数据分区**：大表按时间分区

---

**文档版本历史**
| 版本 | 日期 | 修改说明 | 修改人 |
|------|------|----------|--------|
| v2.0 | 2026-02-18 | 完整数据库设计，覆盖所有核心表 | AI Assistant |
| v1.0 | 2026-02-14 | 初始数据库设计草案 | 架构团队 |

*本文档将随着数据库设计演进持续更新。*
