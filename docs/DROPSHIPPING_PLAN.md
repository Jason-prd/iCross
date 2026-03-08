# iCross 一键代发功能模块

> 创建日期：2026-02-27

---

## 📋 功能概述

### 核心流程
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. 订单同步  │ →  │ 2. 1688自动 │ →  │ 3. 物流回传 │ →  │ 4. 状态更新 │
│ 定时拉取    │    │ 代发下单    │    │ Ozon       │    │ 完成       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 📊 数据对应关系

### Excel 台账字段 → iCross 系统

| Excel 字段 | iCross 字段 | 说明 |
|-----------|-------------|------|
| SKU编号 | platform_sku | Ozon SKU |
| 1688商品名称 | extra_data.1688_name | 1688商品 |
| 1688链接 | extra_data.1688_link | 代发链接 |
| 采购成本 | variant.cost | 成本价 |
| 发货城市 | extra_data.city | 仓库位置 |

---

## 🛠️ 开发计划

### Phase 1: 基础功能

| 功能 | 文件 | 说明 |
|------|------|------|
| 1688代发表 | dropshipping/supplier.py | 代发商信息 |
| 代发关联 | dropshipping/link.py | SKU与1688商品关联 |
| 订单同步 | dropshipping/order_sync.py | 从Ozon拉取订单 |

### Phase 2: 自动化

| 功能 | 说明 |
|------|------|
| 自动下单 | 收到订单自动向1688下单 |
| 物流回传 | 物流单号自动上传Ozon |
| 库存同步 | 定时同步Ozon库存 |

### Phase 3: 智能功能

| 功能 | 说明 |
|------|------|
| 利润计算 | 自动计算订单利润 |
| 异常处理 | 缺货/涨价等异常处理 |
| 报表统计 | 代发数据统计 |

---

## 📁 目录结构

```
backend/app/
├── dropshipping/
│   ├── __init__.py
│   ├── models.py          # 代发数据模型
│   ├── service.py         # 代发服务
│   ├── order_sync.py      # 订单同步
│   ├── supplier.py        # 代发商管理
│   └── tasks.py           # 定时任务
└── api/v1/endpoints/
    └── dropshipping.py    # API接口
```

---

## 🔗 关键数据流

### 1. 订单同步
```
Ozon API → Order → 匹配 PlatformProduct → 找到对应1688商品
```

### 2. 代发下单
```
Order → 获取1688链接 → 自动下单 → 获取物流单号
```

### 3. 物流回传
```
物流单号 → Ozon API → 更新订单配送信息
```

---

## 📝 代发商品数据结构

```python
{
    "sku": "SKU#0512142311-0-0",           # Ozon SKU
    "1688_url": "https://detail.1688.com/offer/640034987890.html",
    "1688_name": "旅行抽真空双肩包...",     # 1688商品名称
    "purchase_cost": 258,                   # 采购成本(元)
    "shipping_cost": 8,                    # 采购运费
    "warehouse": "深圳",                     # 仓库
    "supplier": "王雷",                     # 代发商
    "supplier_phone": "1379798****",       # 代发商电话
}
```

---

## ⚙️ 配置项

| 配置 | 说明 | 默认值 |
|------|------|--------|
| AUTO_DROP_SHIP | 是否自动代发 | false |
| ORDER_SYNC_INTERVAL | 订单同步间隔(分钟) | 5 |
| LOW_STOCK_THRESHOLD | 低库存预警阈值 | 10 |
| PRICE_CHANGE_THRESHOLD | 价格变化阈值(%) | 20 |

---

*规划完成 - 待开发*
