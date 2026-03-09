# -*- coding: utf-8 -*-
"""
SPU and SKU utility functions
"""


def extract_spu(sku: str) -> str:
    """
    Extract SPU from SKU
    SKU#0918932817-1 -> SKU#0918932817
    SKU#0918932817-1-1 -> SKU#0918932817
    SKU#0918392810 -> SKU#0918392810
    """
    if not sku:
        return ""

    # Remove prefix
    if sku.startswith("SKU#"):
        sku = sku[4:]

    # Split by -, take first part as SPU
    parts = sku.split("-")
    if parts:
        return f"SKU#{parts[0]}"

    return f"SKU#{sku}"


def extract_variant_index(sku: str) -> str:
    """
    Extract variant index from SKU
    SKU#0918932817-1 -> 1
    SKU#0918932817-1-1 -> 1-1
    SKU#0918392810 -> 0
    """
    if not sku:
        return "0"

    # Remove prefix
    if sku.startswith("SKU#"):
        sku = sku[4:]

    # Split, take part after - as variant
    parts = sku.split("-")
    if len(parts) > 1:
        return "-".join(parts[1:])

    return "0"


def is_same_spu(sku1: str, sku2: str) -> bool:
    """Check if two SKUs belong to the same SPU"""
    return extract_spu(sku1) == extract_spu(sku2)


# Test
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
