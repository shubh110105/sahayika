from app.models.customer_model import (
    get_customer_profile,
    create_customer_profile,
    update_customer_profile
)


def save_customer_profile(
    customer_id,
    address,
    city,
    state,
    pincode
):
    address = address.strip()
    city = city.strip()
    state = state.strip()
    pincode = pincode.strip()

    if not address:
        return False, "Address is required."

    if not city:
        return False, "City is required."

    if not state:
        return False, "State is required."

    if not pincode:
        return False, "Pincode is required."

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