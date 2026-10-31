
from datetime import date
from app.database import execute_transaction


def record_salary_payment(salary_id, recorded_by, payment_date=None, remarks=None):
    """
    Record payment for a finalized salary record.

    Returns:
        (success, message, payment_id)
    """

    if payment_date is None:
        payment_date = date.today()

    def transaction(cursor):
        # Lock the salary record and verify that it is finalized.
        cursor.execute(
            """
            SELECT salary_id, status
            FROM salary_records
            WHERE salary_id = %s
            FOR UPDATE
            """,
            (salary_id,)
        )

        salary = cursor.fetchone()

        if not salary:
            return False, "Salary record not found.", None

        # Transaction cursor returns tuples.
        if salary[1] != "FINALIZED":
            return False, "Only finalized salary records can be paid.", None

        # Prevent duplicate payment records.
        cursor.execute(
            """
            SELECT payment_id
            FROM payment_records
            WHERE salary_id = %s
            FOR UPDATE
            """,
            (salary_id,)
        )

        existing_payment = cursor.fetchone()

        if existing_payment:
            return False, "A payment record already exists for this salary.", None

        cursor.execute(
            """
            INSERT INTO payment_records (
                salary_id,
                status,
                payment_date,
                recorded_by,
                remarks
            )
            VALUES (%s, 'PAID', %s, %s, %s)
            """,
            (
                salary_id,
                payment_date,
                recorded_by,
                remarks
            )
        )

        payment_id = cursor.lastrowid

        return True, "Salary payment recorded successfully.", payment_id

    return execute_transaction(transaction)
