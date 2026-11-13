"""Read-only Admin attendance overview queries."""

from app.database import fetch_all


def get_attendance_overview(
    attendance_date=None,
    maid_id=None,
    customer_id=None,
    status=None,
):
    """
    Return attendance records with maid/customer details.

    Optional filters:
      - attendance_date: exact date (YYYY-MM-DD or date object)
      - maid_id: positive maid user ID
      - customer_id: positive customer user ID
      - status: one of the attendance table's supported statuses

    This function only reads data. It does not create or modify attendance.
    """

    query = """
        SELECT
            a.attendance_id,
            a.employment_id,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            a.customer_confirmation,
            a.created_at,
            e.customer_id,
            e.maid_id,
            customer_user.full_name AS customer_name,
            maid_user.full_name AS maid_name
        FROM attendance a
        JOIN employments e
            ON e.employment_id = a.employment_id
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        JOIN users maid_user
            ON maid_user.user_id = e.maid_id
    """

    conditions = []
    params = []

    if attendance_date is not None:
        conditions.append("a.attendance_date = %s")
        params.append(attendance_date)

    if maid_id is not None:
        conditions.append("e.maid_id = %s")
        params.append(maid_id)

    if customer_id is not None:
        conditions.append("e.customer_id = %s")
        params.append(customer_id)

    if status is not None:
        allowed_statuses = {
            "PENDING",
            "CONFIRMED",
            "DISPUTED",
            "ADJUSTED",
            "REJECTED",
        }

        normalized_status = str(status).strip().upper()

        if normalized_status not in allowed_statuses:
            raise ValueError("Invalid attendance status filter.")

        conditions.append("a.status = %s")
        params.append(normalized_status)

    if conditions:
        query += "\n        WHERE " + "\n          AND ".join(conditions)

    query += """
        ORDER BY
            a.attendance_date DESC,
            a.attendance_id DESC
    """

    return fetch_all(query, tuple(params))
