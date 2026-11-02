
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
        # Lock assignment and requirement together so their statuses transition atomically.
        cursor.execute(
            """
            SELECT
                ma.assignment_id,
                ma.maid_id,
                ma.status,
                ma.requirement_id,
                ma.previous_requirement_status,
                hr.status
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
            stored_maid_id,
            current_status,
            requirement_id,
            previous_requirement_status,
            requirement_status,
        ) = assignment

        if int(stored_maid_id) != int(maid_id):
            raise ValueError("You are not authorized to respond to this assignment.")

        if current_status != "PENDING_MAID_RESPONSE":
            raise ValueError("This assignment has already been responded to or closed.")

        if requirement_status != "WAITING_FOR_MAID":
            raise ValueError("Requirement status is inconsistent with this assignment.")

        if decision == "REJECT" and previous_requirement_status not in ("SUBMITTED", "UNDER_REVIEW"):
            raise ValueError("The previous requirement status is missing or invalid.")

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

        next_requirement_status = (
            "MAID_ACCEPTED" if decision == "ACCEPT" else previous_requirement_status
        )
        cursor.execute(
            """
            UPDATE household_requirements
            SET status = %s
            WHERE requirement_id = %s
              AND status = 'WAITING_FOR_MAID'
            """,
            (next_requirement_status, requirement_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Requirement status could not be updated after maid response.")

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
