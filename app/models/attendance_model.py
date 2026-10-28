
"""Attendance operations for active maid employments."""

from datetime import date, datetime

from app.database import execute_transaction, fetch_all, fetch_one


def get_maid_attendance(maid_id):
    """Return attendance records for employments owned by this maid."""

    query = """
        SELECT
            a.attendance_id,
            a.employment_id,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status,
            a.customer_confirmation,
            e.customer_id,
            u.full_name AS customer_name
        FROM attendance a
        JOIN employments e
            ON e.employment_id = a.employment_id
        JOIN users u
            ON u.user_id = e.customer_id
        WHERE e.maid_id = %s
        ORDER BY a.attendance_date DESC, a.attendance_id DESC
    """

    return fetch_all(query, (maid_id,))


def record_check_in(maid_id, employment_id, attendance_date=None):
    """Record check-in for the maid's active, scheduled employment."""

    if attendance_date is None:
        attendance_date = date.today()

    if isinstance(attendance_date, str):
        try:
            attendance_date = date.fromisoformat(attendance_date)
        except ValueError:
            return False, "Invalid attendance date.", None

    if not isinstance(attendance_date, date):
        return False, "Invalid attendance date.", None

    def operation(cursor):
        # Lock and validate the employment.
        cursor.execute(
            """
            SELECT
                e.employment_id,
                e.maid_id,
                ma.requirement_id
            FROM employments e
            JOIN maid_assignments ma
                ON ma.assignment_id = e.assignment_id
            WHERE e.employment_id = %s
              AND e.maid_id = %s
              AND e.status = 'ACTIVE'
            FOR UPDATE
            """,
            (employment_id, maid_id),
        )

        employment = cursor.fetchone()

        if not employment:
            raise ValueError("Active employment not found for this maid.")

        _, _, requirement_id = employment

        # Confirm the employment has a schedule on the requested weekday.
        weekday = attendance_date.strftime("%A").upper()

        cursor.execute(
            """
            SELECT schedule_id
            FROM requirement_schedules
            WHERE requirement_id = %s
              AND day_of_week = %s
            LIMIT 1
            """,
            (requirement_id, weekday),
        )

        if not cursor.fetchone():
            raise ValueError("No work is scheduled for this date.")

        # Lock any existing attendance record for this employment and date.
        cursor.execute(
            """
            SELECT attendance_id, check_in
            FROM attendance
            WHERE employment_id = %s
              AND attendance_date = %s
            FOR UPDATE
            """,
            (employment_id, attendance_date),
        )

        existing = cursor.fetchone()

        if existing:
            raise ValueError(
                "Attendance already exists for this employment and date."
            )

        # Create a pending attendance record with the current check-in time.
        cursor.execute(
            """
            INSERT INTO attendance (
                employment_id,
                attendance_date,
                check_in,
                status,
                customer_confirmation
            )
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP,
                'PENDING',
                'PENDING'
            )
            """,
            (employment_id, attendance_date),
        )

        return cursor.lastrowid

    try:
        attendance_id = execute_transaction(operation)
        return True, "Check-in recorded successfully.", attendance_id

    except ValueError as exc:
        return False, str(exc), None

    except Exception as exc:
        # The database unique constraint prevents duplicate daily records.
        # Return a clear message if a database constraint or transaction fails.
        error_message = str(exc).lower()

        if "duplicate" in error_message or "1062" in error_message:
            return (
                False,
                "Attendance already exists for this employment and date.",
                None,
            )

        # Keep unexpected database errors visible in the server logs.
        raise

def record_check_out(maid_id, attendance_id):
    """Record check-out for an attendance record owned by this maid."""

    def operation(cursor):
        cursor.execute(
            """
            SELECT
                a.attendance_id,
                a.check_in,
                a.check_out,
                a.status
            FROM attendance a
            JOIN employments e
                ON e.employment_id = a.employment_id
            WHERE a.attendance_id = %s
              AND e.maid_id = %s
              AND e.status = 'ACTIVE'
            FOR UPDATE
            """,
            (attendance_id, maid_id),
        )

        attendance = cursor.fetchone()

        if not attendance:
            raise ValueError("Attendance record not found for this maid.")

        _, check_in, check_out, status = attendance

        if check_in is None:
            raise ValueError("Check-in must be recorded first.")

        if check_out is not None:
            raise ValueError("Check-out has already been recorded.")

        if status in ("REJECTED", "DISPUTED"):
            raise ValueError(
                "Check-out cannot be recorded for rejected or disputed attendance."
            )

        cursor.execute(
            """
            UPDATE attendance
            SET check_out = CURRENT_TIMESTAMP
            WHERE attendance_id = %s
              AND check_out IS NULL
            """,
            (attendance_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError("Check-out could not be recorded.")

        return attendance_id

    try:
        saved_id = execute_transaction(operation)
        return True, "Check-out recorded successfully.", saved_id

    except ValueError as exc:
        return False, str(exc), None
