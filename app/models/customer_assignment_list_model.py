
"""Database queries for customer assignment listings."""

from app.database import fetch_all


def get_customer_assignments(customer_id):
    """Return assignments for requirements owned by this customer."""

    query = """
        SELECT
            ma.assignment_id,
            ma.requirement_id,
            ma.maid_id,
            ma.status AS assignment_status,
            ma.assigned_at,
            ma.maid_response_at,
            ma.customer_confirmation_at,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.estimated_monthly_salary,
            GROUP_CONCAT(
                DISTINCT s.service_name
                ORDER BY s.service_name
                SEPARATOR ', '
            ) AS services,
            maid_user.full_name AS maid_name

        FROM maid_assignments ma

        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id

        JOIN customer_profiles cp
            ON cp.customer_id = hr.customer_id

        JOIN maid_profiles mp
            ON mp.maid_id = ma.maid_id

        JOIN users maid_user
            ON maid_user.user_id = mp.maid_id

        LEFT JOIN requirement_services rs
            ON rs.requirement_id = hr.requirement_id

        LEFT JOIN services s
            ON s.service_id = rs.service_id

        WHERE cp.customer_id = %s

        GROUP BY
            ma.assignment_id,
            ma.requirement_id,
            ma.maid_id,
            ma.status,
            ma.assigned_at,
            ma.maid_response_at,
            ma.customer_confirmation_at,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.estimated_monthly_salary,
            maid_user.full_name

        ORDER BY ma.assigned_at DESC
    """

    return fetch_all(query, (customer_id,))
