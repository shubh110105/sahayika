
"""Database queries for the Maid assignment dashboard."""

from app.database import fetch_all


def get_maid_assignments(maid_id):
    """Return assignments belonging only to the specified maid."""

    query = """
        SELECT
            ma.assignment_id,
            ma.requirement_id,
            ma.status AS assignment_status,
            ma.assigned_at,
            ma.maid_response_at,

            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.additional_requirements,
            hr.estimated_monthly_salary,

            GROUP_CONCAT(
                DISTINCT s.service_name
                ORDER BY s.service_name
                SEPARATOR ', '
            ) AS services

        FROM maid_assignments ma

        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id

        LEFT JOIN requirement_services rs
            ON rs.requirement_id = hr.requirement_id

        LEFT JOIN services s
            ON s.service_id = rs.service_id

        WHERE ma.maid_id = %s

        GROUP BY
            ma.assignment_id,
            ma.requirement_id,
            ma.status,
            ma.assigned_at,
            ma.maid_response_at,
            hr.location_address,
            hr.city,
            hr.state,
            hr.pincode,
            hr.additional_requirements,
            hr.estimated_monthly_salary

        ORDER BY ma.assigned_at DESC
    """


    return fetch_all(query, (maid_id,))
