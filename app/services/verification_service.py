from app.models.maid_model import get_maid_profile
from app.models.verification_model import (
    get_latest_verification,
    create_verification,
    get_pending_verifications,
    get_verification_by_id,
    update_verification
)


ALLOWED_STATUSES = {
    "VERIFIED",
    "REJECTED",
    "SUSPENDED"
}


def submit_verification(maid_user_id):
    maid = get_maid_profile(maid_user_id)

    if not maid or not maid.get("maid_id"):
        return False, "Complete your maid profile first."

    latest = get_latest_verification(maid["maid_id"])

    if latest and latest["status"] in ("PENDING", "VERIFIED", "SUSPENDED"):
        messages = {
            "PENDING": "A pending request already exists.",
            "VERIFIED": "Your profile is already verified.",
            # A suspended maid must not be able to lift the suspension by
            # simply submitting a new request.
            "SUSPENDED": (
                "Your verification is suspended. Please contact the "
                "administrator."
            ),
        }
        return False, messages[latest["status"]]

    create_verification(maid["maid_id"])

    return True, "Verification request submitted successfully."


def list_pending_verifications():
    return get_pending_verifications()


def review_verification(
    verification_id,
    status,
    remarks,
    admin_user_id
):
    status = status.strip().upper() if isinstance(status, str) else ""
    remarks = remarks.strip() if isinstance(remarks, str) else ""

    if status not in ALLOWED_STATUSES:
        return False, "Invalid verification status."

    verification = get_verification_by_id(verification_id)

    if not verification:
        return False, "Verification request not found."

    if verification["status"] != "PENDING":
        return False, "This request has already been reviewed."

    if status == "REJECTED" and not remarks:
        return False, "Remarks are required when rejecting a request."

    updated = update_verification(
        verification_id=verification_id,
        status=status,
        remarks=remarks or None,
        admin_user_id=admin_user_id
    )

    if not updated:
        # Another admin reviewed the request between our check and update.
        return False, "This request has already been reviewed."

    return True, f"Verification status updated to {status}."