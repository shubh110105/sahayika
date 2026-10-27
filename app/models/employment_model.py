
"""Database operations for final assignment confirmation and employment activation."""

from app.database import execute_transaction


def finalize_assignment(assignment_id, admin_id):
    """
    Finalize a customer-confirmed assignment and create employment atomically.
    Employment becomes active only after final Admin confirmation.
    """

    def operation(cursor):
        # Lock the assignment and its requirement while validating final approval.
        cursor.execute(
            """
            SELECT
                ma.assignment_id,
                ma.requirement_id,
                ma.status,
                hr.customer_id,
                hr.estimated_monthly_salary
            FROM maid_assignments ma
            JOIN household_requirements hr
              ON hr.requirement_id = ma.requirement_id
            WHERE ma.assignment_id = %s
            FOR UPDATE
            """,
            (assignment_id,),
        )

        assignment = cursor.fetchone()

        if not assignment:
            raise ValueError("Assignment not found.")

        (
            stored_assignment_id,
            requirement_id,
            current_status,
            customer_id,
            monthly_salary,
        ) = assignment

        if current_status != "CUSTOMER_CONFIRMED":
            raise ValueError(
                "Only customer-confirmed assignments can be finalized."
            )

        if monthly_salary is None or float(monthly_salary) <= 0:
            raise ValueError(
                "A valid positive salary estimate is required."
            )

        # Ensure this Admin exists and has the correct role and active account.
        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
              AND role = 'ADMIN'
              AND status = 'ACTIVE'
            FOR UPDATE
            """,
            (admin_id,),
        )

        if not cursor.fetchone():
            raise ValueError("An active Admin account is required.")

        # Ensure this assignment has not already generated employment.
        cursor.execute(
            """
            SELECT employment_id
            FROM employments
            WHERE assignment_id = %s
            FOR UPDATE
            """,
            (stored_assignment_id,),
        )

        if cursor.fetchone():
            raise ValueError("Employment already exists for this assignment.")

        # Finalize the assignment before creating employment in this transaction.
        cursor.execute(
            """
            UPDATE maid_assignments
            SET status = 'ADMIN_CONFIRMED',
                admin_confirmation_at = CURRENT_TIMESTAMP
            WHERE assignment_id = %s
              AND status = 'CUSTOMER_CONFIRMED'
            """,
            (stored_assignment_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError("Final Admin confirmation could not be saved.")

        # Create the active employment using the saved requirement salary.
        cursor.execute(
            """
            INSERT INTO employments (
                assignment_id,
                customer_id,
                maid_id,
                start_date,
                monthly_salary,
                status
            )
            SELECT
                ma.assignment_id,
                hr.customer_id,
                ma.maid_id,
                CURRENT_DATE,
                hr.estimated_monthly_salary,
                'ACTIVE'
            FROM maid_assignments ma
            JOIN household_requirements hr
              ON hr.requirement_id = ma.requirement_id
            WHERE ma.assignment_id = %s
              AND ma.status = 'ADMIN_CONFIRMED'
              AND hr.customer_id = %s
              AND hr.estimated_monthly_salary > 0
            """,
            (stored_assignment_id, customer_id),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Employment could not be created from the saved salary estimate."
            )

        return cursor.lastrowid

    try:
        employment_id = execute_transaction(operation)
        return True, "Assignment finalized and employment activated.", employment_id

    except ValueError as exc:
        return False, str(exc), None
