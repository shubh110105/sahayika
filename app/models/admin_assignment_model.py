
"""Database queries for Admin assignment review."""

from app.database import fetch_all


def get_assignments_pending_admin_confirmation():
    """Return assignments confirmed by the customer and awaiting Admin."""

    query = """
        SELECT
            ma.assignment_id,
            ma.requirement_id,
            ma.maid_id,
            ma.status AS assignment_status,
            ma.customer_confirmation_at,

            hr.customer_id,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.estimated_monthly_salary,

            customer_user.full_name AS customer_name,
            maid_user.full_name AS maid_name,

            GROUP_CONCAT(
                DISTINCT s.service_name
                ORDER BY s.service_name
                SEPARATOR ', '
            ) AS services

        FROM maid_assignments ma

        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id

        JOIN customer_profiles cp
            ON cp.customer_id = hr.customer_id

        JOIN users customer_user
            ON customer_user.user_id = cp.customer_id

        JOIN maid_profiles mp
            ON mp.maid_id = ma.maid_id

        JOIN users maid_user
            ON maid_user.user_id = mp.maid_id

        LEFT JOIN requirement_services rs
            ON rs.requirement_id = hr.requirement_id

        LEFT JOIN services s
            ON s.service_id = rs.service_id

        WHERE ma.status = 'CUSTOMER_CONFIRMED'

        GROUP BY
            ma.assignment_id,
            ma.requirement_id,
            ma.maid_id,
            ma.status,
            ma.customer_confirmation_at,
            hr.customer_id,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.estimated_monthly_salary,
            customer_user.full_name,
            maid_user.full_name

        ORDER BY ma.customer_confirmation_at ASC
    """

    return fetch_all(query)
