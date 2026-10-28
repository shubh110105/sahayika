
"""Database queries for customer attendance review."""

from app.database import fetch_all


def get_customer_attendance(customer_id):
    """Return attendance records belonging to this customer's employments."""

    query = """
        SELECT
            a.attendance_id,
            a.employment_id,
            e.maid_id,
            maid_user.full_name AS maid_name,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            a.customer_confirmation
        FROM attendance a
        JOIN employments e
            ON e.employment_id = a.employment_id
        JOIN users maid_user
            ON maid_user.user_id = e.maid_id
        WHERE e.customer_id = %s
        ORDER BY a.attendance_date DESC, a.attendance_id DESC
    """

    return fetch_all(query, (customer_id,))



def confirm_customer_attendance(customer_id, attendance_id, decision, reason=None):
    """Confirm or dispute attendance belonging to the customer's employment."""

    from app.database import execute_transaction

    if decision not in ("CONFIRMED", "DISPUTED"):
        return False, "Invalid attendance decision."

    if decision == "DISPUTED" and not (reason and reason.strip()):
        return False, "Please provide a reason for disputing attendance."

    def transaction(cursor):
        # Verify that this attendance belongs to the logged-in customer.
        cursor.execute(
            """
            SELECT a.attendance_id, a.check_in, a.check_out,
                   a.customer_confirmation
            FROM attendance a
            JOIN employments e ON e.employment_id = a.employment_id
            WHERE a.attendance_id = %s
              AND e.customer_id = %s
            FOR UPDATE
            """,
            (attendance_id, customer_id)
        )
        record = cursor.fetchone()

        if not record:
            raise ValueError("Attendance record not found.")

        if not record[1] or not record[2]:
            raise ValueError("Attendance must have both check-in and check-out.")

        if record[3] != "PENDING":
            raise ValueError("This attendance has already been reviewed.")

        if decision == "CONFIRMED":
            cursor.execute(
                """
                UPDATE attendance
                SET customer_confirmation = 'CONFIRMED',
                    status = 'CONFIRMED'
                WHERE attendance_id = %s
                """,
                (attendance_id,)
            )
        else:
            cursor.execute(
                """
                UPDATE attendance
                SET customer_confirmation = 'DISPUTED',
                    status = 'DISPUTED'
                WHERE attendance_id = %s
                """,
                (attendance_id,)
            )

            cursor.execute(
                """
                INSERT INTO attendance_disputes
                    (attendance_id, customer_reason, status)
                VALUES (%s, %s, 'OPEN')
                """,
                (attendance_id, reason.strip())
            )

        return True, "Attendance " + decision.lower() + " successfully."

    try:
        return execute_transaction(transaction)
    except ValueError as exc:
        return False, str(exc)
