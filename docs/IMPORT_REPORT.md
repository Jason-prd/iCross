# iCross Ozon 商品导入与一键代发功能规划

> 生成日期：2026-02-27

---

## 📊 数据匹配结果

### Excel 台账数据
| Sheet | 记录数 | 说明 |
|-------|--------|------|
| 0. 选品 | 413 | 待选品 |
| 1. 详情 | 4,988 | 商品详细信息 |
| 2. 定价 | 4,507 | 采购/物流/利润 |
| 3. 上架 | 3,933 | 上架状态 |

### Ozon 店铺数据
- **店铺商品总数**: 449
- **SKU 格式**: `SKU#0518224537-1`

### 匹配结果
- ✅ **匹配成功**: 448 个商品
- ❌ **未匹配**: 1 个 (SKU#0618000000)

---

## 📋 匹配商品数据结构

每个匹配的商品包含：

| 字段 | 来源 | 说明 |
|------|------|------|
| sku | Excel+Ozon | SKU编号 |
| 1688_name | Excel | 1688商品名称 |
| ozon_name | Excel | Ozon商品名称 |
| ozon_name_ru | Excel | 俄文名称 |
| category | Excel | 商品类目 |
| sku_name | Excel | 规格名称 |
| price_cny | Excel | 采购价(元) |
| stock | Excel | 1688库存 |
| purchase_cost | Excel | 采购成本 |
| shipping_cost | Excel | 采购运费 |
| delivery_standard | Excel | 标准配送成本 |
| delivery_economy | Excel | 经济配送成本 |
| profit_standard | Excel | 标准利润率 |
| profit_economy | Excel | 经济利润率 |
| ozon_price | Ozon | Ozon售价 |
| ozon_quantity | Ozon | Ozon库存 |
| ozon_product_id | Ozon | Ozon商品ID |
| listing_status | Excel | 上架状态 |
| listing_shop | Excel | 上架店铺 |

---

## 🛠️ iCross 数据模型

### 现有模型对应

| iCross 模型 | 对应数据 |
|-------------|---------|
| Shop | 店铺 (Ozon) |
| Product | 主商品 |
| ProductVariant | SKU/变体 |
| PlatformProduct | Ozon商品 |
| Order | 订单 |

---

## 📦 一键代发功能设计

### 核心流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 订单同步    │ →  │ 1688自动   │ →  │ 物流回传   │ →  │ 状态更新    │
│ (Ozon)     │    │ 下单       │    │ Ozon       │    │ 完成       │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 需要开发的功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **1. 商品导入** | 从Excel导入商品数据到系统 | P0 |
| **2. 1688关联** | 关联1688商品链接/代发商 | P0 |
| **3. 订单同步** | 自动同步Ozon新订单 | P0 |
| **4. 代发下单** | 收到订单自动向1688下单 | P1 |
| **5. 物流回传** | 物流单号自动回传Ozon | P1 |
| **6. 库存同步** | 定时同步Ozon库存到系统 | P1 |
| **7. 利润计算** | 自动计算订单利润 | P2 |

---

## 📊 匹配商品数据样本

```json
{
  "sku": "SKU#0828104003-1-16",
  "1688_name": "透明手机壳...",
  "ozon_name": "透明手机壳...",
  "ozon_name_ru": "nan",
  "category": "手机配件 > 手机套",
  "sku_name": "透明-13Promax",
  "price_cny": 16,
  "stock": 666,
  "purchase_cost": 16,
  "shipping_cost": 4,
  "delivery_standard": 4.975,
  "profit_standard": 0.38,
  "ozon_price": 0,
  "ozon_quantity": 0,
  "ozon_product_id": 2616248911
}
```

---

## 🚀 下一步行动

1. **启动数据库服务** - 需要启动 PostgreSQL
2. **运行导入脚本** - 将448个商品导入系统
3. **开发一键代发** - 基于导入的数据实现自动化

---

*报告生成完成 - 2026-02-27*
