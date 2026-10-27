
"""Database queries for viewing active employment records."""

from app.database import fetch_all


def get_active_employments():
    """Return active employments with customer and maid details."""

    query = """
        SELECT
            e.employment_id,
            e.assignment_id,
            e.customer_id,
            e.maid_id,
            e.start_date,
            e.monthly_salary,
            e.status AS employment_status,
            hr.requirement_id,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            customer_user.full_name AS customer_name,
            maid_user.full_name AS maid_name
        FROM employments e
        JOIN household_requirements hr
            ON hr.requirement_id = (
                SELECT ma.requirement_id
                FROM maid_assignments ma
                WHERE ma.assignment_id = e.assignment_id
            )
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        JOIN users maid_user
            ON maid_user.user_id = e.maid_id
        WHERE e.status = 'ACTIVE'
        ORDER BY e.start_date DESC, e.employment_id DESC
    """

    return fetch_all(query)
