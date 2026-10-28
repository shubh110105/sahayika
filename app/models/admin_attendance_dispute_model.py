
"""Database queries for Admin attendance dispute review."""

from app.database import fetch_all


def get_all_attendance_disputes():
    """Return attendance disputes with related maid and customer details."""

    query = """
        SELECT
            d.dispute_id,
            d.attendance_id,
            d.customer_reason,
            d.maid_response,
            d.admin_decision,
            d.status AS dispute_status,
            d.resolved_by,
            d.created_at,
            d.resolved_at,
            a.employment_id,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            e.customer_id,
            e.maid_id,
            customer_user.full_name AS customer_name,
            maid_user.full_name AS maid_name
        FROM attendance_disputes d
        JOIN attendance a
            ON a.attendance_id = d.attendance_id
        JOIN employments e
            ON e.employment_id = a.employment_id
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        JOIN users maid_user
            ON maid_user.user_id = e.maid_id
        ORDER BY
            CASE WHEN d.status IN ('OPEN', 'MAID_RESPONDED',
                                   'UNDER_REVIEW')
                 THEN 0 ELSE 1 END,
            d.created_at DESC
    """

    return fetch_all(query)
