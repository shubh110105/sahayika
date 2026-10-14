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

    if latest and latest["status"] in ("PENDING", "VERIFIED"):
        return False, (
            "A pending request already exists."
            if latest["status"] == "PENDING"
            else "Your profile is already verified."
        )

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
    status = status.strip().upper()
    remarks = (remarks or "").strip()

    if status not in ALLOWED_STATUSES:
        return False, "Invalid verification status."

    verification = get_verification_by_id(verification_id)

    if not verification:
        return False, "Verification request not found."

    if verification["status"] != "PENDING":
        return False, "This request has already been reviewed."

    if status == "REJECTED" and not remarks:
        return False, "Remarks are required when rejecting a request."

    update_verification(
        verification_id=verification_id,
        status=status,
        remarks=remarks or None,
        admin_user_id=admin_user_id
    )

    return True, f"Verification status updated to {status}."