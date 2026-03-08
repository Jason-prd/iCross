# -*- coding: utf-8 -*-
"""
提取SPU和SKU的工具函数
"""

def extract_spu(sku: str) -> str:
    """
    从SKU提取SPU
    SKU#0918932817-1 -> SKU#0918932817
    SKU#0918932817-1-1 -> SKU#0918932817
    SKU#0918392810 -> SKU#0918392810
    """
    if not sku:
        return ""
    
    # 移除前缀
    if sku.startswith("SKU#"):
        sku = sku[4:]
    
    # 按-分割，取第一部分作为SPU
    parts = sku.split("-")
    if parts:
        return f"SKU#{parts[0]}"
    
    return f"SKU#{sku}"


def extract_variant_index(sku: str) -> str:
    """
    从SKU提取变体索引
    SKU#0918932817-1 -> 1
    SKU#0918932817-1-1 -> 1-1
    SKU#0918392810 -> 0
    """
    if not sku:
        return "0"
    
    # 移除前缀
    if sku.startswith("SKU#"):
        sku = sku[4:]
    
    # 分割，取-后面的部分
    parts = sku.split("-")
    if len(parts) > 1:
        return "-".join(parts[1:])
    
    return "0"


def is_same_spu(sku1: str, sku2: str) -> bool:
    """判断两个SKU是否属于同一个SPU"""
    return extract_spu(sku1) == extract_spu(sku2)


# 测试
if __name__ == "__main__":
    test_skus = [
        "SKU#0918392810",
        "SKU#0918932817-1",
        "SKU#0918932817-1-1",
        "SKU#0918932817-2",
        "SKU#0523235411-5-0",
    ]
    
    for sku in test_skus:
        spu = extract_spu(sku)
        variant = extract_variant_index(sku)
        print(f"{sku} -> SPU: {spu}, Variant: {variant}")
