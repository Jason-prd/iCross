#!/usr/bin/env python3
"""
更新用户密码哈希以匹配security模块
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3

# 只导入必要的模块，避免SQLAlchemy关系
from app.core.security import get_password_hash, verify_password


def main():
    db_path = "icross_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有用户
    cursor.execute("SELECT id, email, password_hash FROM users")
    users = cursor.fetchall()

    for user_id, email, current_hash in users:
        print(f"Processing user: {email}")

        # 根据电子邮件确定密码
        if email == "admin@icross.com":
            plain_password = "admin123"
        elif email == "test@icross.com":
            plain_password = "test123"
        else:
            print("  Skipping unknown user")
            continue

        # 使用security模块验证当前哈希
        try:
            if verify_password(plain_password, current_hash):
                print("  Password already correct")
                continue
        except Exception as e:
            print(f"  Verification failed: {e}")

        # 生成新哈希
        new_hash = get_password_hash(plain_password)
        print("  Updating password hash")

        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id)
        )

    conn.commit()

    # 验证更新
    cursor.execute("SELECT email, password_hash FROM users")
    for email, hash in cursor.fetchall():
        print(f"User {email}: hash={hash[:20]}...")

    conn.close()
    print("Password update complete")


if __name__ == "__main__":
    main()
