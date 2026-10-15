
from app.database import fetch_one


def is_maid_eligible_for_assignment(maid_id):
    query = """
        SELECT
            (
                SELECT mv.status
                FROM maid_verifications mv
                WHERE mv.maid_id = mp.maid_id
                ORDER BY mv.verification_id DESC
                LIMIT 1
            ) AS verification_status
        FROM maid_profiles mp
        WHERE mp.maid_id = %s
    """

    maid = fetch_one(query, (maid_id,))

    if not maid:
        return False

    return maid["verification_status"] == "VERIFIED"
