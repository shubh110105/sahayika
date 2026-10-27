from app.database import fetch_one, execute_query




def get_maid_profile(user_id):
    query = """
        SELECT
            u.user_id,
            u.full_name,
            u.email,
            u.phone,
            u.role,
            u.status,

            mp.maid_id,
            mp.address,
            mp.city,
            mp.state,
            mp.pincode,
            mp.experience_years,
            mp.bio,
            mp.profile_status,

            (
                SELECT mv.status
                FROM maid_verifications mv
                WHERE mv.maid_id = mp.maid_id
                ORDER BY mv.verification_id DESC
                LIMIT 1
            ) AS verification_status

        FROM users u
        LEFT JOIN maid_profiles mp
            ON u.user_id = mp.maid_id
        WHERE u.user_id = %s
    """

    return fetch_one(query, (user_id,))



def create_maid_profile(
    user_id,
    address,
    city,
    pincode,
    experience_years,
    bio
):
    query = """
        INSERT INTO maid_profiles
        (
            maid_id,
            address,
            city,
            pincode,
            experience_years,
            bio,
            profile_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'COMPLETE')
    """

    return execute_query(
        query,
        (
            user_id,
            address,
            city,
            pincode,
            experience_years,
            bio
        )
    )


def update_maid_profile(
    user_id,
    address,
    city,
    pincode,
    experience_years,
    bio
):
    query = """
        UPDATE maid_profiles
        SET
            address = %s,
            city = %s,
            pincode = %s,
            experience_years = %s,
            bio = %s,
            profile_status = 'COMPLETE'
        WHERE maid_id = %s
    """

    return execute_query(
        query,
        (
            address,
            city,
            pincode,
            experience_years,
            bio,
            user_id
        )
    )