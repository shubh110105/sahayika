
"""Database operations for maid service management."""

from app.database import fetch_all, execute_query


def get_all_services():
    """Return all available platform services."""
    query = """
        SELECT service_id, service_name
        FROM services
        ORDER BY service_id
    """
    return fetch_all(query)


def get_maid_services(maid_id):
    """Return the services currently registered by a maid."""
    query = """
        SELECT
            ms.service_id,
            s.service_name,
            ms.experience_level
        FROM maid_services ms
        JOIN services s
            ON s.service_id = ms.service_id
        WHERE ms.maid_id = %s
        ORDER BY s.service_id
    """
    return fetch_all(query, (maid_id,))


def save_maid_services(maid_id, selected_services):
    """Replace a maid's service selections with the submitted selections."""

    # Remove duplicates while preserving the submitted order.
    selected_ids = list(dict.fromkeys(selected_services))

    # Validate every requested service before changing the database.
    if selected_ids:
        placeholders = ", ".join(["%s"] * len(selected_ids))
        query = f"""
            SELECT service_id
            FROM services
            WHERE service_id IN ({placeholders})
        """
        existing = fetch_all(query, tuple(selected_ids))
        existing_ids = {int(row["service_id"]) for row in existing}

        if existing_ids != set(selected_ids):
            return False, "One or more selected services are invalid."

    # Replace the service list in a transaction so a failure rolls back.
    from app.database import execute_transaction

    def operation(cursor):
        cursor.execute(
            "DELETE FROM maid_services WHERE maid_id = %s",
            (maid_id,)
        )

        for service_id in selected_ids:
            cursor.execute(
                """
                INSERT INTO maid_services
                    (maid_id, service_id, experience_level)
                VALUES (%s, %s, %s)
                """,
                (maid_id, service_id, "Experienced")
            )

        return True

    try:
        execute_transaction(operation)
        return True, "Maid services saved successfully."
    except Exception:
        return False, "Unable to save maid services."
