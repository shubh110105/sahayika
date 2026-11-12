from mysql.connector import IntegrityError

from app.models.user_model import get_user_by_email, create_user
from app.validators import (
    MIN_PASSWORD_LENGTH,
    clean_text,
    is_valid_email,
    is_valid_phone,
)


ALLOWED_ROLES = {"CUSTOMER", "MAID"}


def register_user(full_name, email, phone, password, role):
    full_name = clean_text(full_name)
    email = clean_text(email).lower()
    phone = clean_text(phone)

    if not full_name:
        return False, "Full name is required."

    if not email:
        return False, "Email is required."

    if not is_valid_email(email):
        return False, "Enter a valid email address."

    if not phone:
        return False, "Phone number is required."

    if not is_valid_phone(phone):
        return False, "Enter a valid phone number (10 to 15 digits)."

    # Passwords are never trimmed: spaces may be part of the password.
    if not isinstance(password, str) or not password:
        return False, "Password is required."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, (
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )

    if not isinstance(role, str) or role not in ALLOWED_ROLES:
        return False, "Invalid registration role."

    existing_user = get_user_by_email(email)

    if existing_user:
        return False, "An account with this email already exists."

    try:
        user_id = create_user(
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )
    except IntegrityError:
        # Two sign-ups with the same email can race past the check above;
        # the database's unique constraint is the final guard.
        return False, "An account with this email already exists."

    return True, user_id
