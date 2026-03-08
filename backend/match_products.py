# -*- coding: utf-8 -*-
import pandas as pd
import json
import sys
from pathlib import Path

# Read Excel
excel_file = pd.ExcelFile(r'C:\Users\lijia\Desktop\ozon台账.xlsx')

# Load all sheets
details_df = pd.read_excel(excel_file, sheet_name='1. 详情')
pricing_df = pd.read_excel(excel_file, sheet_name='2. 定价')
listing_df = pd.read_excel(excel_file, sheet_name='3. 上架')

# Load Ozon products
with open(r'D:\iCross\backend\ozon_products.json', 'r', encoding='utf-8') as f:
    ozon_products = json.load(f)

print(f"Excel - 详情 sheet: {len(details_df)} rows")
print(f"Excel - 定价 sheet: {len(pricing_df)} rows")
print(f"Excel - 上架 sheet: {len(listing_df)} rows")
print(f"Ozon products: {len(ozon_products)}")

# Extract offer_ids from Ozon
ozon_offer_ids = set()
for p in ozon_products:
    offer_id = p.get('offer_id', '')
    if offer_id:
        ozon_offer_ids.add(offer_id)

print(f"\nOzon unique offer_ids: {len(ozon_offer_ids)}")

# Find matching SKUs in Excel Details sheet
# The SKU column name is like 'SKU#0915222047-3'
sku_columns = [col for col in details_df.columns if col.startswith('SKU#')]
print(f"SKU columns in Details: {len(sku_columns)}")

# Get all unique SKUs from Details sheet
excel_skus = set()
for col in sku_columns:
    skus = details_df[col].dropna().unique()
    for sku in skus:
        if isinstance(sku, str) and sku.startswith('SKU#'):
            excel_skus.add(sku)

print(f"Excel unique SKUs in Details: {len(excel_skus)}")

# Find matching SKUs
matched_skus = ozon_offer_ids.intersection(excel_skus)
print(f"\nMatched SKUs (in both Ozon and Excel): {len(matched_skus)}")

# Find Ozon-only SKUs (in Ozon but not in Excel)
ozon_only = ozon_offer_ids - excel_skus
print(f"Ozon-only SKUs (in Ozon, not in Excel): {len(ozon_only)}")

# Show some examples
print(f"\n=== Sample matched SKUs ===")
for sku in list(matched_skus)[:10]:
    print(f"  {sku}")

print(f"\n=== Sample Ozon-only SKUs ===")
for sku in list(ozon_only)[:10]:
    print(f"  {sku}")

# Now let's get detailed info for matched products
# We need to find the row in Excel for each matched SKU
print(f"\n=== Building product database ===")

products_data = []

for sku in matched_skus:
    # Find this SKU in Details sheet
    # Check each SKU column
    product_info = {'sku': sku}
    
    for col in sku_columns:
        matches = details_df[details_df[col] == sku]
        if not matches.empty:
            row = matches.iloc[0]
            product_info['1688_name'] = row.get('1688商品名称', '')
            product_info['ozon_name'] = row.get('OZON商品名称', '')
            product_info['ozon_name_ru'] = row.get('OZON商品名称（俄文）', '')
            product_info['category'] = row.get('类目', '')
            product_info['sku_name'] = row.get('规格名称', '')
            product_info['price_cny'] = row.get('价格，CNY*', 0)
            product_info['stock'] = row.get('SKU库存', 0)
            product_info['city'] = row.get('发货城市', '')
            product_info['weight_g'] = row.get('重量(g)', 0)
            product_info['1688_link'] = row.get('备注', '')
            break
    
    # Find in pricing sheet
    pricing_matches = pricing_df[pricing_df['SKU编号'] == sku]
    if not pricing_matches.empty:
        row = pricing_matches.iloc[0]
        product_info['purchase_cost'] = row.get('采购成本', 0)
        product_info['shipping_cost'] = row.get('采购运费', 0)
        product_info['delivery_standard'] = row.get('配送成本-standard', 0)
        product_info['delivery_economy'] = row.get('配送成本-economy', 0)
        product_info['profit_standard'] = row.get('利润率-standard', 0)
        product_info['profit_economy'] = row.get('利润率-economy', 0)
    
    # Find in listing sheet
    listing_matches = listing_df[listing_df['SKU编号（已上架）'] == sku]
    if not listing_matches.empty:
        row = listing_matches.iloc[0]
        product_info['listing_status'] = row.get('上架状态', '')
        product_info['listing_shop'] = row.get('上架店铺', '')
    
    # Get current Ozon info
    for p in ozon_products:
        if p.get('offer_id') == sku:
            product_info['ozon_price'] = p.get('price', 0)
            product_info['ozon_quantity'] = p.get('stock', 0)
            product_info['ozon_product_id'] = p.get('id') or p.get('product_id')
            break
    
    products_data.append(product_info)

print(f"\n=== Products with complete data: {len(products_data)} ===")

# Save to file
with open('matched_products.json', 'w', encoding='utf-8') as f:
    json.dump(products_data, f, ensure_ascii=False, indent=2)

print(f"\nSaved matched products to matched_products.json")

# Show sample
print(f"\n=== Sample matched product ===")
if products_data:
    sample = products_data[0]
    for k, v in sample.items():
        print(f"  {k}: {v}")
