
"""Database operations for customer assignment confirmation."""

from app.database import execute_transaction


def confirm_maid_assignment(assignment_id, customer_id):
    """
    Allow the requirement-owning customer to confirm an assignment
    after the maid has accepted it.
    """

    def operation(cursor):
        # Lock the assignment while validating and updating it.
        cursor.execute(
            """
            SELECT
                ma.assignment_id,
                ma.status,
                hr.customer_id
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

        # The transaction cursor returns tuples.
        stored_assignment_id, current_status, requirement_customer_id = assignment

        if int(requirement_customer_id) != int(customer_id):
            raise ValueError(
                "You are not authorized to confirm this assignment."
            )

        if current_status != "MAID_ACCEPTED":
            raise ValueError(
                "Only an assignment accepted by the maid can be confirmed."
            )

        cursor.execute(
            """
            UPDATE maid_assignments
            SET status = 'CUSTOMER_CONFIRMED',
                customer_confirmation_at = CURRENT_TIMESTAMP
            WHERE assignment_id = %s
              AND status = 'MAID_ACCEPTED'
            """,
            (stored_assignment_id,),
        )

        if cursor.rowcount != 1:
            raise ValueError("Customer confirmation could not be saved.")

        return True

    try:
        execute_transaction(operation)
        return True, "Assignment confirmed by the customer."

    except ValueError as exc:
        return False, str(exc)
