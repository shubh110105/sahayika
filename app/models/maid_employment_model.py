
"""Database queries for a maid's active employments."""

from app.database import fetch_all


def get_maid_active_employments(maid_id):
    """Return active employments belonging only to this maid."""

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
            customer_user.full_name AS customer_name
        FROM employments e
        JOIN maid_assignments ma
            ON ma.assignment_id = e.assignment_id
        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        WHERE e.maid_id = %s
          AND e.status = 'ACTIVE'
        ORDER BY e.start_date DESC, e.employment_id DESC
    """

    return fetch_all(query, (maid_id,))
