"""Small, dependency-free input helpers shared by the service layer.

Every helper accepts any JSON value (including None, numbers or lists)
so a malformed request returns a clean validation error instead of
crashing with an AttributeError.
"""

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")

MIN_PASSWORD_LENGTH = 8
MAX_EXPERIENCE_YEARS = 60


def clean_text(value):
    """Return a stripped string, or "" for None / non-string values."""
    if isinstance(value, str):
        return value.strip()
    return ""


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email)) and len(email) <= 254


def is_valid_phone(phone):
    # Allow common separators typed by users, then check the digits.
    compact = re.sub(r"[\s\-()]", "", phone)
    return bool(PHONE_PATTERN.match(compact))


def is_valid_pincode(pincode):
    """Indian pincodes are exactly six digits."""
    return pincode.isdigit() and len(pincode) == 6


def parse_experience_years(value):
    """Return (years, error_message). Accepts 3, "3" or "3.0"."""
    if isinstance(value, bool) or value is None:
        return None, "Experience must be a number."

    try:
        number = float(str(value).strip())
    except ValueError:
        return None, "Experience must be a number."

    if number != number or number in (float("inf"), float("-inf")):
        return None, "Experience must be a number."

    if number < 0:
        return None, "Experience cannot be negative."

    if number > MAX_EXPERIENCE_YEARS:
        return None, (
            f"Experience cannot be more than {MAX_EXPERIENCE_YEARS} years."
        )

    if number != int(number):
        return None, "Experience must be a whole number of years."

    return int(number), None
