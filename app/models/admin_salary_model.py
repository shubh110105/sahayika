"""Database operations for Admin monthly salary management."""

from datetime import date

from app.database import execute_transaction


def generate_monthly_salary(employment_id, salary_month):
    """
    Create a draft salary record for an active employment.

    salary_month must be the first day of the target month.
    """
    if not isinstance(salary_month, date):
        return False, "A valid salary month is required.", None

    salary_month = salary_month.replace(day=1)

    def transaction(cursor):
        cursor.execute(
            """
            SELECT employment_id, monthly_salary
            FROM employments
            WHERE employment_id = %s
              AND status = 'ACTIVE'
            FOR UPDATE
            """,
            (employment_id,)
        )

        employment = cursor.fetchone()

        if not employment:
            raise ValueError("Active employment not found.")

        base_salary = employment[1]

        cursor.execute(
            """
            INSERT INTO salary_records (
                employment_id,
                salary_month,
                base_salary,
                attendance_adjustment,
                leave_adjustment,
                other_adjustment,
                final_salary,
                status
            )
            VALUES (%s, %s, %s, 0, 0, 0, %s, 'DRAFT')
            """,
            (
                employment_id,
                salary_month,
                base_salary,
                base_salary
            )
        )

        return cursor.lastrowid

    try:
        salary_id = execute_transaction(transaction)
        return True, "Draft salary record generated successfully.", salary_id

    except ValueError as exc:
        return False, str(exc), None

    except Exception as exc:
        # Duplicate employment-month records are prevented by the DB constraint.
        if "uq_salary_employment_month" in str(exc):
            return False, "A salary record already exists for this employment and month.", None

        raise

def update_draft_salary_adjustments(
    salary_id,
    attendance_adjustment,
    leave_adjustment,
    other_adjustment,
    other_adjustment_reason=None
):
    """Update adjustments on a draft salary record."""

    def transaction(cursor):
        cursor.execute(
            """
            SELECT salary_id, status
            FROM salary_records
            WHERE salary_id = %s
            FOR UPDATE
            """,
            (salary_id,)
        )

        salary_record = cursor.fetchone()

        if not salary_record:
            raise ValueError("Salary record not found.")

        if salary_record[1] != "DRAFT":
            raise ValueError("Only draft salary records can be adjusted.")

        if other_adjustment != 0 and not (
            isinstance(other_adjustment_reason, str)
            and other_adjustment_reason.strip()
        ):
            raise ValueError(
                "A reason is required for an other adjustment."
            )

        cursor.execute(
            """
            UPDATE salary_records
            SET
                attendance_adjustment = %s,
                leave_adjustment = %s,
                other_adjustment = %s,
                final_salary = (
                    base_salary
                    + %s
                    + %s
                    + %s
                )
            WHERE salary_id = %s
              AND status = 'DRAFT'
            """,
            (
                attendance_adjustment,
                leave_adjustment,
                other_adjustment,
                attendance_adjustment,
                leave_adjustment,
                other_adjustment,
                salary_id
            )
        )

        return True

    try:
        execute_transaction(transaction)
        return True, "Draft salary adjustments updated successfully."

    except ValueError as exc:
        return False, str(exc)

def finalize_salary_record(salary_id):
    """Finalize a draft salary record."""

    def transaction(cursor):
        cursor.execute(
            """
            SELECT salary_id, status, final_salary
            FROM salary_records
            WHERE salary_id = %s
            FOR UPDATE
            """,
            (salary_id,)
        )

        salary_record = cursor.fetchone()

        if not salary_record:
            raise ValueError("Salary record not found.")

        if salary_record[1] != "DRAFT":
            raise ValueError("Only draft salary records can be finalized.")

        if salary_record[2] < 0:
            raise ValueError("Final salary cannot be negative.")

        cursor.execute(
            """
            UPDATE salary_records
            SET status = 'FINALIZED'
            WHERE salary_id = %s
              AND status = 'DRAFT'
            """,
            (salary_id,)
        )

        return True

    try:
        execute_transaction(transaction)
        return True, "Salary record finalized successfully."

    except ValueError as exc:
        return False, str(exc)