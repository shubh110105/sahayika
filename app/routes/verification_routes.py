from flask import Blueprint, jsonify, session

from app.role_required import role_required
from app.services.verification_service import submit_verification
from app.models.maid_model import get_maid_profile
from app.models.verification_model import get_latest_verification


# Maid-facing verification endpoints. The Admin review screens live in
# admin_routes.py (/admin/verifications...).
verification = Blueprint(
    "verification",
    __name__,
    url_prefix="/verification"
)


@verification.route("/submit", methods=["POST"])
@role_required("MAID")
def submit():
    user_id = session["user_id"]

    success, message = submit_verification(user_id)

    return jsonify({
        "success": success,
        "message": message
    }), 200 if success else 400


@verification.route("/status", methods=["GET"])
@role_required("MAID")
def status():
    maid = get_maid_profile(session["user_id"])

    if not maid or not maid.get("maid_id"):
        return jsonify({
            "success": False,
            "message": "Complete your maid profile first."
        }), 404

    record = get_latest_verification(maid["maid_id"])

    return jsonify({
        "success": True,
        "verification": record
    })
