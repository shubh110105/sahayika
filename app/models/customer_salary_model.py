from app.database import fetch_all


def get_customer_salary_records(customer_id):
    """
    Return finalized salary records for employments belonging
    to the specified customer, including payment details.
    """
    query = """
        SELECT
            sr.salary_id,
            sr.employment_id,
            sr.salary_month,
            sr.base_salary,
            sr.attendance_adjustment,
            sr.leave_adjustment,
            sr.other_adjustment,
            sr.final_salary,
            sr.status AS salary_status,
            sr.created_at AS salary_created_at,
            pr.status AS payment_status,
            pr.payment_date,
            pr.remarks AS payment_remarks
        FROM salary_records AS sr
        INNER JOIN employments AS e
            ON e.employment_id = sr.employment_id
        LEFT JOIN payment_records AS pr
            ON pr.salary_id = sr.salary_id
        WHERE e.customer_id = %s
          AND sr.status = 'FINALIZED'
        ORDER BY sr.salary_month DESC, sr.salary_id DESC
    """

    return fetch_all(query, (customer_id,))