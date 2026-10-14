import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import fetch_one, execute_query
from app.auth_utils import hash_password


ADMIN_EMAIL = "admin@maidmate.com"
ADMIN_PASSWORD = "Admin@12345"


def create_admin():
    existing_admin = fetch_one(
        """
        SELECT user_id
        FROM users
        WHERE email = %s
        """,
        (ADMIN_EMAIL,)
    )

    if existing_admin:
        print("Admin account already exists.")
        print("User ID:", existing_admin["user_id"])
        return

    password_hash = hash_password(ADMIN_PASSWORD)

    user_id = execute_query(
        """
        INSERT INTO users
        (
            full_name,
            email,
            phone,
            password_hash,
            role
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "MaidMate Administrator",
            ADMIN_EMAIL,
            "9000000000",
            password_hash,
            "ADMIN"
        )
    )

    print("Admin account created successfully.")
    print("User ID:", user_id)
    print("Email:", ADMIN_EMAIL)


if __name__ == "__main__":
    create_admin()