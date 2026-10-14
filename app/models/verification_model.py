from app.database import fetch_one, fetch_all, execute_query


def get_latest_verification(maid_id):
    query = """
        SELECT
            verification_id,
            maid_id,
            status,
            remarks,
            submitted_at,
            verified_at,
            verified_by
        FROM maid_verifications
        WHERE maid_id = %s
        ORDER BY verification_id DESC
        LIMIT 1
    """

    return fetch_one(query, (maid_id,))


def create_verification(maid_id):
    query = """
        INSERT INTO maid_verifications (maid_id)
        VALUES (%s)
    """

    return execute_query(query, (maid_id,))


def get_pending_verifications():
    query = """
        SELECT
            mv.verification_id,
            mv.maid_id,
            mv.status,
            mv.remarks,
            mv.submitted_at,
            mp.maid_id,
            u.full_name,
            u.email,
            u.phone,
            mp.city,
            mp.pincode,
            mp.experience_years,
            mp.bio
        FROM maid_verifications mv
        JOIN maid_profiles mp
            ON mv.maid_id = mp.maid_id
        JOIN users u
            ON mp.maid_id = u.user_id
        WHERE mv.status = 'PENDING'
        ORDER BY mv.submitted_at ASC
    """

    return fetch_all(query)


def get_verification_by_id(verification_id):
    query = """
        SELECT
            verification_id,
            maid_id,
            status,
            remarks,
            submitted_at,
            verified_at,
            verified_by
        FROM maid_verifications
        WHERE verification_id = %s
    """

    return fetch_one(query, (verification_id,))


def update_verification(
    verification_id,
    status,
    remarks,
    admin_user_id
):
    query = """
        UPDATE maid_verifications
        SET
            status = %s,
            remarks = %s,
            verified_at = CURRENT_TIMESTAMP,
            verified_by = %s
        WHERE verification_id = %s
    """

    return execute_query(
        query,
        (status, remarks, admin_user_id, verification_id)
    )