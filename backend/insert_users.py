#!/usr/bin/env python3
"""
直接插入测试用户到数据库，避免SQLAlchemy关系问题
"""

import sqlite3
import uuid
from datetime import datetime

# 手动计算bcrypt哈希，避免passlib问题
import bcrypt


def get_password_hash(password: str) -> str:
    # bcrypt.gensalt() 默认rounds=12
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def main():
    db_path = "icross_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查现有用户
    cursor.execute(
        "SELECT email FROM users WHERE email IN ('admin@icross.com', 'test@icross.com')"
    )
    existing = [row[0] for row in cursor.fetchall()]
    print("Existing users:", existing)

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
            print(f"User {email} already exists, skipping")
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
                1,  # email_verified as boolean (1 for true)
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

        # 验证密码
        verify_ok = verify_password(user_data["password"], password_hash)
        print(
            f"Created user {email} successfully, ID: {user_id}, password verified: {verify_ok}"
        )

    conn.commit()

    # 验证插入的用户
    cursor.execute("SELECT id, email, name FROM users")
    print("\nAll users in database:")
    for row in cursor.fetchall():
        print(f"  {row}")

    conn.close()
    print("\nTest users created successfully!")


if __name__ == "__main__":
    main()
