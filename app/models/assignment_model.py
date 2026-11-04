
"""Database operations for Admin-controlled maid assignments."""

from app.database import execute_transaction
from app.models.matching_model import (
    BLOCKING_ASSIGNMENT_STATUSES as BLOCKING_STATUSES,
    candidate_has_assignment_conflict,
    get_maid_shortlist,
    get_required_schedules,
)


def create_maid_assignment(requirement_id, maid_id, admin_id):
    """
    Create a pending assignment for a maid currently on the eligible shortlist.

    This does not create employment. Employment must only be created
    after the maid accepts, the customer confirms, and the Admin
    gives final confirmation.
    """

    # Validate the candidate using the existing matching rules.
    requirement, candidates, message = get_maid_shortlist(requirement_id)

    if requirement is None:
        return False, message, None

    candidate = next(
        (
            item for item in candidates
            if int(item["maid_id"]) == int(maid_id)
        ),
        None,
    )

    if candidate is None:
        return (
            False,
            "The selected maid is not currently eligible for this requirement.",
            None,
        )

    def operation(cursor):
        # Lock the requirement row while checking and creating the assignment.
        cursor.execute(
            """
            SELECT requirement_id, status
            FROM household_requirements
            WHERE requirement_id = %s
            FOR UPDATE
            """,
            (requirement_id,),
        )
        locked_requirement = cursor.fetchone()

        if not locked_requirement:
            raise ValueError("Requirement not found.")

        # The transaction cursor returns tuples, not dictionaries.
        requirement_status = locked_requirement[1]

        if requirement_status not in ("SUBMITTED", "UNDER_REVIEW"):
            raise ValueError(
                "This requirement is no longer available for assignment."
            )

        # Serialize assignments per maid: take a lock on the maid's user row,
        # then re-check for schedule clashes. Without this, two admins could
        # book the same maid for two overlapping requirements at once (the
        # shortlist check above is done before any lock is held).
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s FOR UPDATE",
            (maid_id,),
        )
        cursor.fetchone()

        if candidate_has_assignment_conflict(
            maid_id, requirement_id, get_required_schedules(requirement_id)
        ):
            raise ValueError(
                "The selected maid was just assigned to an overlapping "
                "requirement."
            )

        # Prevent a second active/pending assignment for this requirement.
        placeholders = ", ".join(["%s"] * len(BLOCKING_STATUSES))

        cursor.execute(
            f"""
            SELECT assignment_id
            FROM maid_assignments
            WHERE requirement_id = %s
              AND status IN ({placeholders})
            LIMIT 1
            FOR UPDATE
            """,
            (requirement_id, *BLOCKING_STATUSES),
        )

        if cursor.fetchone():
            raise ValueError(
                "This requirement already has a pending or confirmed assignment."
            )

        # Prevent the same maid from receiving a duplicate active assignment
        # for this requirement.
        cursor.execute(
            f"""
            SELECT assignment_id
            FROM maid_assignments
            WHERE requirement_id = %s
              AND maid_id = %s
              AND status IN ({placeholders})
            LIMIT 1
            FOR UPDATE
            """,
            (requirement_id, maid_id, *BLOCKING_STATUSES),
        )

        if cursor.fetchone():
            raise ValueError(
                "This maid already has an active assignment for this requirement."
            )

        cursor.execute(
            """
            INSERT INTO maid_assignments (
                requirement_id,
                maid_id,
                assigned_by,
                status,
                previous_requirement_status
            )
            VALUES (%s, %s, %s, 'PENDING_MAID_RESPONSE', %s)
            """,
            (requirement_id, maid_id, admin_id, requirement_status),
        )

        assignment_id = cursor.lastrowid

        # Keep the requirement lifecycle in sync within this transaction.
        cursor.execute(
            """
            UPDATE household_requirements
            SET status = 'WAITING_FOR_MAID'
            WHERE requirement_id = %s
              AND status = %s
            """,
            (requirement_id, requirement_status),
        )

        if cursor.rowcount != 1:
            raise ValueError("Requirement status could not be updated for assignment.")

        return assignment_id

    try:
        assignment_id = execute_transaction(operation)
        return (
            True,
            "Assignment created. Awaiting the maid's response.",
            assignment_id,
        )
    except ValueError as exc:
        return False, str(exc), None
