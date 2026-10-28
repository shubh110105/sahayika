
"""Database queries for maid attendance dispute responses."""

from app.database import fetch_all, execute_transaction


def get_maid_attendance_disputes(maid_id):
    """Return disputes associated only with this maid's employments."""

    query = """
        SELECT
            d.dispute_id,
            d.attendance_id,
            d.customer_reason,
            d.maid_response,
            d.admin_decision,
            d.status AS dispute_status,
            d.created_at,
            d.resolved_at,
            a.employment_id,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            customer_user.full_name AS customer_name
        FROM attendance_disputes d
        JOIN attendance a
            ON a.attendance_id = d.attendance_id
        JOIN employments e
            ON e.employment_id = a.employment_id
        JOIN users customer_user
            ON customer_user.user_id = e.customer_id
        WHERE e.maid_id = %s
        ORDER BY d.created_at DESC, d.dispute_id DESC
    """

    return fetch_all(query, (maid_id,))


def submit_maid_dispute_response(maid_id, dispute_id, response_text):
    """Submit a response to an open dispute belonging to this maid."""

    if not response_text or not response_text.strip():
        return False, "Please enter a response."

    response_text = response_text.strip()

    def transaction(cursor):
        cursor.execute(
            """
            SELECT d.dispute_id, d.status, d.maid_response
            FROM attendance_disputes d
            JOIN attendance a
                ON a.attendance_id = d.attendance_id
            JOIN employments e
                ON e.employment_id = a.employment_id
            WHERE d.dispute_id = %s
              AND e.maid_id = %s
            FOR UPDATE
            """,
            (dispute_id, maid_id)
        )

        dispute = cursor.fetchone()

        if not dispute:
            raise ValueError("Dispute not found.")

        if dispute[1] not in ("OPEN", "MAID_RESPONDED"):
            raise ValueError("This dispute is no longer accepting responses.")

        if dispute[2]:
            raise ValueError("A response has already been submitted.")

        cursor.execute(
            """
            UPDATE attendance_disputes
            SET maid_response = %s,
                status = 'MAID_RESPONDED'
            WHERE dispute_id = %s
            """,
            (response_text, dispute_id)
        )

        return True, "Response submitted successfully."

    try:
        return execute_transaction(transaction)
    except ValueError as exc:
        return False, str(exc)
