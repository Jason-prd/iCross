# iCross API对接与功能完善总结

> 更新日期：2026-02-27

---

## ✅ 已完成

### 1. 后端API

| API端点 | 路径 | 功能 |
|---------|------|------|
| 选品管理 | `/api/v1/selection` | 获取选品列表、统计、详情、上架 |
| 代发订单 | `/api/v1/dropship` | 代发订单CRUD、处理、发货 |
| 运营仪表盘 | `/api/v1/dashboard` | 统计数据、低库存、最近订单 |
| Ozon商品 | `/api/v1/ozon/products` | 商品列表、详情、同步 |

### 2. 前端页面

| 页面 | 路径 | 状态 |
|------|------|------|
| 运营仪表盘 | `/dashboard/new` | ✅ 已连接API |
| 选品管理 | `/products/selection` | ✅ 已连接API |
| Ozon商品 | `/products/ozon/new` | ✅ 已连接API |
| 订单管理 | `/orders/new` | ✅ 已连接API |
| 代发订单 | `/orders/dropship` | ✅ 已连接API |

### 3. API服务层

- `frontend/src/services/api.ts` - 封装所有API调用

---

## 📋 数据字段对应

### 选品管理

| 前端字段 | 后端字段 | 来源 |
|----------|----------|------|
| master_sku | master_sku | Product |
| title | title | Product |
| selection_status | selection_status | Product |
| listing_status | listing_status | Product |
| source_url | source_url | Product |
| source_price | source_price | Product |
| source_supplier | source_supplier | Product |

### Ozon商品

| 前端字段 | 后端字段 | 来源 |
|----------|----------|------|
| sku | platform_sku | PlatformProduct |
| ozon_price | platform_price | PlatformProduct |
| ozon_stock | platform_stock | PlatformProduct |
| ozon_product_id | platform_product_id | PlatformProduct |
| profit_rate | (计算) | PlatformProduct |

### 代发订单

| 前端字段 | 后端字段 | 来源 |
|----------|----------|------|
| platform_order_id | platform_order_id | DropshipOrder |
| sku | sku | DropshipOrder |
| sale_price | sale_price | DropshipOrder |
| purchase_cost | purchase_cost | DropshipOrder |
| profit | profit | DropshipOrder |
| tracking_number | tracking_number | DropshipOrder |

---

## 🔄 数据流程

```
Excel台账 → 匹配商品 → 导入系统 → 选品管理
                                    ↓
                              商品上架(Ozon)
                                    ↓
                              订单同步(Ozon)
                                    ↓
                              创建代发订单
                                    ↓
                              1688下单(待实现)
                                    ↓
                              物流回传Ozon
```

---

## 📝 待完善

### 1. 1688 API对接
- 需要申请1688开放平台API
- 实现自动下单功能

### 2. 定时任务配置
- 配置Celery
- 实现自动同步

### 3. 通知功能
- 微信/邮件通知
- 低库存预警

### 4. 数据分析
- 销售报表
- 利润分析

---

## 🚀 启动指南

### 后端
```bash
cd D:\iCross\backend
uvicorn app.main:app --reload --port 8000
```

### 前端
```bash
cd D:\iCross\frontend
npm run dev
```

### 访问
- 后端API文档: http://localhost:8000/api/v1/docs
- 前端: http://localhost:5173
