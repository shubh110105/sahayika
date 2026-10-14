from app.database import fetch_one, execute_query


def get_customer_profile(user_id):
    query = """
        SELECT
            u.user_id,
            u.full_name,
            u.email,
            u.phone,
            u.role,
            u.status,
           cp.customer_id,
           cp.address,
           cp.city,
           cp.state,
           cp.pincode,
           cp.updated_at
        FROM users u
        LEFT JOIN customer_profiles cp
            ON u.user_id = cp.customer_id
        WHERE u.user_id = %s
    """

    return fetch_one(query, (user_id,))


def create_customer_profile(
    customer_id,
    address,
    city,
    state,
    pincode
):
    query = """
        INSERT INTO customer_profiles
        (
            customer_id,
            address,
            city,
            state,
            pincode
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    return execute_query(
        query,
        (
            customer_id,
            address,
            city,
            state,
            pincode
        )
    )


def update_customer_profile(
    customer_id,
    address,
    city,
    state,
    pincode
):
    query = """
        UPDATE customer_profiles
        SET
            address = %s,
            city = %s,
            state = %s,
            pincode = %s
        WHERE customer_id = %s
    """

    return execute_query(
        query,
        (
            address,
            city,
            state,
            pincode,
            customer_id
        )
    )