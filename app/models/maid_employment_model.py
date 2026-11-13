
"""Database queries for a maid's active employments."""

from app.database import fetch_all



def get_maid_active_employments(maid_id):
    """Return active employments and their schedules for this maid."""

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
            rs.day_of_week,
            rs.start_time AS schedule_start_time,
            rs.end_time AS schedule_end_time
        FROM employments e
        JOIN maid_assignments ma
            ON ma.assignment_id = e.assignment_id
        JOIN household_requirements hr
            ON hr.requirement_id = ma.requirement_id
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        LEFT JOIN requirement_schedules rs
            ON rs.requirement_id = hr.requirement_id
        WHERE e.maid_id = %s
          AND e.status = 'ACTIVE'
        ORDER BY
            e.start_date DESC,
            e.employment_id DESC,
            FIELD(
                rs.day_of_week,
                'MONDAY',
                'TUESDAY',
                'WEDNESDAY',
                'THURSDAY',
                'FRIDAY',
                'SATURDAY',
                'SUNDAY'
            )
    """

    rows = fetch_all(query, (maid_id,))

    # Group schedule rows under their respective employments.
    employment_map = {}

    for row in rows:
        employment_id = row["employment_id"]

        if employment_id not in employment_map:
            employment_map[employment_id] = {
                key: value
                for key, value in row.items()
                if key not in (
                    "day_of_week",
                    "schedule_start_time",
                    "schedule_end_time"
                )
            }
            employment_map[employment_id]["schedule"] = []

        if row["day_of_week"] is not None:
            employment_map[employment_id]["schedule"].append({
                "day": row["day_of_week"],
                "start_time": str(row["schedule_start_time"]),
                "end_time": str(row["schedule_end_time"])
            })

    return list(employment_map.values())

