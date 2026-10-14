from app.models.maid_model import (
    get_maid_profile,
    create_maid_profile,
    update_maid_profile
)


def save_maid_profile(
    user_id,
    address,
    city,
    pincode,
    experience_years,
    bio
):
    address = address.strip()
    city = city.strip()
    pincode = pincode.strip()
    bio = bio.strip()

    if not address:
        return False, "Address is required."

    if not city:
        return False, "City is required."

    if not pincode:
        return False, "Pincode is required."

    try:
        experience_years = int(experience_years)
    except (TypeError, ValueError):
        return False, "Experience must be a number."

    if experience_years < 0:
        return False, "Experience cannot be negative."

    existing_profile = get_maid_profile(user_id)

    if existing_profile and existing_profile["maid_id"]:
        update_maid_profile(
            user_id,
            address,
            city,
            pincode,
            experience_years,
            bio
        )

        return True, "Maid profile updated successfully."

    create_maid_profile(
        user_id,
        address,
        city,
        pincode,
        experience_years,
        bio
    )

    return True, "Maid profile created successfully."