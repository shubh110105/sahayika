from app.models.maid_model import (
    get_maid_profile,
    create_maid_profile,
    update_maid_profile
)
from app.validators import clean_text, is_valid_pincode, parse_experience_years


def save_maid_profile(
    user_id,
    address,
    city,
    pincode,
    experience_years,
    bio
):
    address = clean_text(address)
    city = clean_text(city)
    pincode = clean_text(pincode)
    bio = clean_text(bio)

    if not address:
        return False, "Address is required."

    if not city:
        return False, "City is required."

    if not pincode:
        return False, "Pincode is required."

    # Same rule as the customer profile and household requirement form.
    if not is_valid_pincode(pincode):
        return False, "Enter a valid 6-digit pincode."

    experience_years, error = parse_experience_years(experience_years)

    if error:
        return False, error

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
