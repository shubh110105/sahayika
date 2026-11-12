from app.models.customer_model import (
    get_customer_profile,
    create_customer_profile,
    update_customer_profile
)
from app.validators import clean_text, is_valid_pincode


def save_customer_profile(
    customer_id,
    address,
    city,
    state,
    pincode
):
    address = clean_text(address)
    city = clean_text(city)
    state = clean_text(state)
    pincode = clean_text(pincode)

    if not address:
        return False, "Address is required."

    if not city:
        return False, "City is required."

    if not state:
        return False, "State is required."

    if not pincode:
        return False, "Pincode is required."

    # Same rule as the household requirement form.
    if not is_valid_pincode(pincode):
        return False, "Enter a valid 6-digit pincode."

    existing_profile = get_customer_profile(customer_id)

    if existing_profile and existing_profile["customer_id"]:
        update_customer_profile(
            customer_id,
            address,
            city,
            state,
            pincode
        )

        return True, "Customer profile updated successfully."

    create_customer_profile(
        customer_id,
        address,
        city,
        state,
        pincode
    )

    return True, "Customer profile created successfully."
