"""Create the first Admin account.

Usage:
    python scripts/create_admin.py

The email defaults to admin@maidmate.com; set ADMIN_EMAIL / ADMIN_PASSWORD
in the environment to override, otherwise the password is asked for.
"""

import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import fetch_one, execute_query
from app.auth_utils import hash_password
from app.validators import MIN_PASSWORD_LENGTH


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@maidmate.com").strip().lower()


def create_admin():
    existing_admin = fetch_one(
        "SELECT user_id FROM users WHERE email = %s",
        (ADMIN_EMAIL,)
    )

    if existing_admin:
        print("Admin account already exists.")
        print("User ID:", existing_admin["user_id"])
        return

    password = os.getenv("ADMIN_PASSWORD") or getpass.getpass(
        "Choose an Admin password: "
    )

    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        sys.exit(1)

    user_id = execute_query(
        """
        INSERT INTO users
        (full_name, email, phone, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "Administrator",
            ADMIN_EMAIL,
            "9000000000",
            hash_password(password),
            "ADMIN"
        )
    )

    print("Admin account created successfully.")
    print("User ID:", user_id)
    print("Email:", ADMIN_EMAIL)


if __name__ == "__main__":
    create_admin()
