#!/usr/bin/env python3
"""
创建测试用户脚本
直接使用SQLite数据库插入用户，避免SQLAlchemy关系问题
"""

import sqlite3
import uuid
from datetime import datetime

from passlib.context import CryptContext

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def main():
    db_path = "icross_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查用户表结构
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print("用户表列:", columns)

    # 检查现有用户
    cursor.execute(
        "SELECT email FROM users WHERE email IN ('admin@icross.com', 'test@icross.com')"
    )
    existing = [row[0] for row in cursor.fetchall()]
    print("已存在用户:", existing)

    # 创建测试用户
    test_users = [
        {
            "email": "admin@icross.com",
            "password": "admin123",
            "name": "Admin",
            "role": "super_admin",
        },
        {
            "email": "test@icross.com",
            "password": "test123",
            "name": "Test User",
            "role": "admin",
        },
    ]

    for user_data in test_users:
        email = user_data["email"]
        if email in existing:
            print(f"用户 {email} 已存在，跳过")
            continue

        user_id = str(uuid.uuid4())
        password_hash = get_password_hash(user_data["password"])
        now = datetime.utcnow().isoformat()

        # 插入用户
        cursor.execute(
            """
            INSERT INTO users (id, email, email_verified, password_hash, name, 
                              timezone, language, currency, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                email,
                True,
                password_hash,
                user_data["name"],
                "Asia/Shanghai",
                "zh-CN",
                "CNY",
                "active",
                now,
                now,
            ),
        )

        # 检查团队是否存在，如果不存在则创建
        cursor.execute("SELECT id FROM teams WHERE name = ?", ("Admin Team",))
        team_row = cursor.fetchone()
        if team_row:
            team_id = team_row[0]
        else:
            team_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO teams (id, name, description, settings, subscription_plan, 
                                  subscription_status, max_members, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    team_id,
                    "Admin Team",
                    "Default admin team",
                    "{}",
                    "basic",
                    "active",
                    5,
                    now,
                    now,
                ),
            )

        # 创建团队成员关系
        member_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO team_members (id, team_id, user_id, role, permissions, status, joined_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                member_id,
                team_id,
                user_id,
                user_data["role"],
                "{}",
                "active",
                now,
                now,
                now,
            ),
        )

        print(f"创建用户 {email} 成功，ID: {user_id}")

    conn.commit()
    conn.close()
    print("测试用户创建完成")


if __name__ == "__main__":
    main()
