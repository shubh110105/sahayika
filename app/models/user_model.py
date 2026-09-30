from app.database import fetch_one, execute_query
from app.auth_utils import hash_password


def get_user_by_email(email):
    query = """
        SELECT
            user_id,
            full_name,
            email,
            phone,
            password_hash,
            role,
            status,
            created_at,
            updated_at
        FROM users
        WHERE email = %s
    """

    return fetch_one(query, (email,))


def get_user_by_id(user_id):
    query = """
        SELECT
            user_id,
            full_name,
            email,
            phone,
            password_hash,
            role,
            status,
            created_at,
            updated_at
        FROM users
        WHERE user_id = %s
    """

    return fetch_one(query, (user_id,))


def create_user(full_name, email, phone, password, role):
    password_hash = hash_password(password)

    query = """
        INSERT INTO users
        (full_name, email, phone, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
    """

    return execute_query(
        query,
        (full_name, email, phone, password_hash, role)
    )