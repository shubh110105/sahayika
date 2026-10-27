# app/services/eligibility_service.py
# Shared eligibility gate for assignment-related workflows.

from app.database import fetch_one


def is_maid_eligible_for_assignment(maid_id):
    """A maid must have an active account, complete profile, and latest VERIFIED status."""
    maid = fetch_one(
        """
        SELECT
            u.status AS account_status,
            mp.profile_status,
            (
                SELECT mv.status
                FROM maid_verifications mv
                WHERE mv.maid_id = mp.maid_id
                ORDER BY mv.verification_id DESC
                LIMIT 1
            ) AS verification_status
        FROM maid_profiles mp
        JOIN users u ON u.user_id = mp.maid_id
        WHERE mp.maid_id = %s
          AND u.role = 'MAID'
        """,
        (maid_id,),
    )

    if not maid:
        return False

    return (
        maid["account_status"] == "ACTIVE"
        and maid["profile_status"] == "COMPLETE"
        and maid["verification_status"] == "VERIFIED"
    )
