from app.models.user_model import get_user_by_email, create_user


ALLOWED_ROLES = {"CUSTOMER", "MAID"}


def register_user(full_name, email, phone, password, role):
    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if not full_name:
        return False, "Full name is required."

    if not email:
        return False, "Email is required."

    if not phone:
        return False, "Phone number is required."

    if not password:
        return False, "Password is required."

    if role not in ALLOWED_ROLES:
        return False, "Invalid registration role."

    existing_user = get_user_by_email(email)

    if existing_user:
        return False, "An account with this email already exists."

    user_id = create_user(
        full_name=full_name,
        email=email,
        phone=phone,
        password=password,
        role=role
    )

    return True, user_id