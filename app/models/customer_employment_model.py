
"""Database queries for a customer's active employments."""

from app.database import fetch_all


def get_customer_active_employments(customer_id):
    """Return active employments belonging only to this customer."""

    query = """
        SELECT
            e.employment_id,
            e.assignment_id,
            e.customer_id,
            e.maid_id,
            e.start_date,
            e.monthly_salary,
            e.status AS employment_status,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            maid_user.full_name AS maid_name
        FROM employments e
        JOIN maid_assignments ma
            ON ma.assignment_id = e.assignment_id
        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id
        JOIN users maid_user
            ON maid_user.user_id = e.maid_id
        WHERE e.customer_id = %s
          AND e.status = 'ACTIVE'
        ORDER BY e.start_date DESC, e.employment_id DESC
    """

    return fetch_all(query, (customer_id,))
