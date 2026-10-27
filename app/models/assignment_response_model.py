
"""Database operations for maid assignment responses."""

from app.database import execute_transaction


def respond_to_assignment(assignment_id, maid_id, decision):
    """
    Allow the assigned maid to accept or reject a pending assignment.
    The maid can respond only to their own assignment.
    """

    allowed_decisions = {
        "ACCEPT": "MAID_ACCEPTED",
        "REJECT": "MAID_REJECTED",
    }

    if decision not in allowed_decisions:
        return False, "Invalid decision."

    new_status = allowed_decisions[decision]

    def operation(cursor):
        # Lock the assignment row to prevent simultaneous responses.
        cursor.execute(
            """
            SELECT assignment_id, maid_id, status
            FROM maid_assignments
            WHERE assignment_id = %s
            FOR UPDATE
            """,
            (assignment_id,),
        )

        assignment = cursor.fetchone()

        if not assignment:
            raise ValueError("Assignment not found.")

        # The transaction cursor returns tuples, not dictionaries.
        stored_assignment_id, stored_maid_id, current_status = assignment

        if int(stored_maid_id) != int(maid_id):
            raise ValueError("You are not authorized to respond to this assignment.")

        if current_status != "PENDING_MAID_RESPONSE":
            raise ValueError("This assignment has already been responded to or closed.")

        cursor.execute(
            """
            UPDATE maid_assignments
            SET status = %s,
                maid_response_at = CURRENT_TIMESTAMP
            WHERE assignment_id = %s
              AND maid_id = %s
              AND status = 'PENDING_MAID_RESPONSE'
            """,
            (new_status, stored_assignment_id, maid_id),
        )

        if cursor.rowcount != 1:
            raise ValueError("Assignment response could not be saved.")

        return True

    try:
        execute_transaction(operation)
        message = (
            "Assignment accepted."
            if decision == "ACCEPT"
            else "Assignment rejected."
        )
        return True, message

    except ValueError as exc:
        return False, str(exc)
