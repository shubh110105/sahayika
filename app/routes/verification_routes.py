from flask import Blueprint, jsonify, request, session, render_template

from app.role_required import role_required
from app.services.verification_service import (
    submit_verification,
    list_pending_verifications,
    review_verification
)
from app.models.maid_model import get_maid_profile
from app.models.verification_model import get_latest_verification


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


@verification.route("/admin/pending", methods=["GET"])
@role_required("ADMIN")
def pending():
    records = list_pending_verifications()

    return jsonify({
        "success": True,
        "verifications": records
    })


@verification.route("/admin/<int:verification_id>/review", methods=["POST"])
@role_required("ADMIN")
def review(verification_id):
    data = request.get_json(silent=True) or {}

    status_value = data.get("status", "")
    remarks = data.get("remarks", "")

    success, message = review_verification(
        verification_id=verification_id,
        status=status_value,
        remarks=remarks,
        admin_user_id=session["user_id"]
    )

    return jsonify({
        "success": success,
        "message": message
    }), 200 if success else 400

@verification.route("/admin/page")
@role_required("ADMIN")
def admin_page():
    return render_template("admin/verifications.html")