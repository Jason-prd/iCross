#!/usr/bin/env python3
"""
创建测试数据
"""

import random
import sqlite3
import uuid
from datetime import datetime, timedelta


def main():
    db_path = "icross_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取团队ID
    cursor.execute("SELECT id FROM teams LIMIT 1")
    team_row = cursor.fetchone()
    if not team_row:
        print("No team found, creating one...")
        team_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO teams (id, name, description, settings, subscription_plan, subscription_status, max_members, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                team_id,
                "Test Team",
                "Test team for development",
                "{}",
                "basic",
                "active",
                5,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
    else:
        team_id = team_row[0]

    print(f"Using team: {team_id}")

    # 创建仓库
    warehouses = []
    for i, name in enumerate(["主仓库", "备用仓库"]):
        warehouse_id = str(uuid.uuid4())
        warehouses.append(warehouse_id)
        cursor.execute(
            """
            INSERT OR IGNORE INTO warehouses (id, team_id, name, code, type, status, settings, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                warehouse_id,
                team_id,
                name,
                f"WH{i+1}",
                "physical",
                "active",
                "{}",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
    print(f"Created {len(warehouses)} warehouses")

    # 创建店铺
    shops = []
    shop_data = [
        ("Ozon旗舰店", "ozon"),
        ("Amazon美国店", "amazon"),
        ("Shopify独立站", "shopify"),
    ]
    for name, platform in shop_data:
        shop_id = str(uuid.uuid4())
        shops.append(shop_id)
        cursor.execute(
            """
            INSERT OR IGNORE INTO shops (id, team_id, name, platform, api_credentials, settings, sync_settings, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                shop_id,
                team_id,
                name,
                platform,
                "{}",
                "{}",
                '{"sync_enabled": true}',
                "active",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
    print(f"Created {len(shops)} shops")

    # 创建商品
    products = []
    product_names = [
        ("无线蓝牙耳机", "BT-001"),
        ("智能手表", "SW-002"),
        ("便携充电宝", "PB-003"),
        ("机械键盘", "KB-004"),
        ("电竞鼠标", "MS-005"),
        ("显示器支架", "ST-006"),
        ("USB集线器", "HB-007"),
        ("手机支架", "PH-008"),
    ]

    for title, sku in product_names:
        product_id = str(uuid.uuid4())
        products.append(product_id)
        cursor.execute(
            """
            INSERT OR IGNORE INTO products (id, team_id, master_sku, title, description, main_image_url, status, images, tags, attributes, extra_data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                product_id,
                team_id,
                sku,
                title,
                f"{title} - 高品质产品",
                f"https://picsum.photos/seed/{sku}/200/200",
                "active",
                "[]",
                "[]",
                "{}",
                "{}",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
    print(f"Created {len(products)} products")

    # 创建库存
    for i, product_id in enumerate(products):
        for warehouse_id in warehouses[:1]:  # 只在主仓库有库存
            quantity = random.randint(0, 200)
            safety_stock = 20
            cursor.execute(
                """
                INSERT OR IGNORE INTO inventory (id, team_id, product_id, warehouse_id, quantity, reserved_quantity, safety_stock, created_at, last_updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(uuid.uuid4()),
                    team_id,
                    product_id,
                    warehouse_id,
                    quantity,
                    random.randint(0, 10),
                    safety_stock,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )
    print("Created inventory records")

    # 创建客户
    customers = []
    customer_names = [
        ("张三", "zhangsan@example.com", "13800138001"),
        ("李四", "lisi@example.com", "13800138002"),
        ("王五", "wangwu@example.com", "13800138003"),
        ("赵六", "zhaoliu@example.com", "13800138004"),
        ("钱七", "qianqi@example.com", "13800138005"),
    ]
    for name, email, phone in customer_names:
        customer_id = str(uuid.uuid4())
        customers.append(customer_id)
        cursor.execute(
            """
            INSERT OR IGNORE INTO customers (id, team_id, name, email, phone, customer_type, level, tags, total_orders, total_spent, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                customer_id,
                team_id,
                name,
                email,
                phone,
                "retail",
                random.choice(["normal", "silver", "gold", "vip"]),
                "[]",
                random.randint(1, 10),
                random.uniform(100, 5000),
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
            ),
        )
    print(f"Created {len(customers)} customers")

    # 创建订单
    statuses = ["pending", "confirmed", "shipped", "delivered"]
    payment_statuses = ["pending", "paid"]
    fulfillment_statuses = ["unfulfilled", "fulfilled"]

    for i in range(15):
        order_id = str(uuid.uuid4())
        shop_id = random.choice(shops)
        customer_id = random.choice(customers) if random.random() > 0.3 else None
        status = random.choice(statuses)
        payment_status = (
            "paid"
            if status in ["confirmed", "shipped", "delivered"]
            else random.choice(payment_statuses)
        )
        fulfillment_status = (
            "fulfilled"
            if status == "delivered"
            else ("fulfilled" if status == "shipped" else "unfulfilled")
        )

        subtotal = random.uniform(50, 500)
        shipping = random.uniform(0, 20)
        total = subtotal + shipping

        created_at = (
            datetime.utcnow() - timedelta(days=random.randint(0, 30))
        ).isoformat()

        cursor.execute(
            """
            INSERT OR IGNORE INTO orders (id, team_id, shop_id, platform_order_id, order_number, customer_id, customer_name, customer_email, shipping_address, currency, subtotal_amount, shipping_amount, tax_amount, discount_amount, total_amount, payment_status, fulfillment_status, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                order_id,
                team_id,
                shop_id,
                f"PO-{100000+i}",
                f"ORD-{2024000+i}",
                customer_id,
                random.choice(["张三", "李四", "王五", "赵六", "钱七", None]),
                random.choice(["customer@example.com", None]),
                '{"city": "北京", "address1": "朝阳区xxx街道"}',
                "CNY",
                subtotal,
                shipping,
                0,
                0,
                total,
                payment_status,
                fulfillment_status,
                status,
                created_at,
                created_at,
            ),
        )

        # 创建订单商品
        product_id = random.choice(products)
        cursor.execute(
            """
            INSERT OR IGNORE INTO order_items (id, order_id, product_id, title, sku, quantity, unit_price, subtotal, total_amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(uuid.uuid4()),
                order_id,
                product_id,
                "商品",
                f"SKU-{random.randint(100,999)}",
                random.randint(1, 3),
                random.uniform(50, 200),
                subtotal,
                subtotal,
                created_at,
            ),
        )

    print("Created 15 orders")

    conn.commit()
    conn.close()
    print("\nTest data created successfully!")


if __name__ == "__main__":
    main()
