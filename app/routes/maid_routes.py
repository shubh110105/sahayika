from flask import Blueprint, request, jsonify, session, render_template

from app.role_required import role_required
from app.models.maid_model import get_maid_profile
from app.services.maid_service import save_maid_profile


maid = Blueprint(
    "maid",
    __name__,
    url_prefix="/maid"
)


@maid.route("/profile", methods=["GET"])
@role_required("MAID")
def get_profile():
    user_id = session["user_id"]

    profile = get_maid_profile(user_id)

    if not profile:
        return jsonify({
            "success": False,
            "message": "Maid not found."
        }), 404

    return jsonify({
        "success": True,
        "profile": profile
    })


@maid.route("/profile", methods=["POST"])
@role_required("MAID")
def save_profile():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    user_id = session["user_id"]

    success, message = save_maid_profile(
        user_id=user_id,
        address=data.get("address", ""),
        city=data.get("city", ""),
        pincode=data.get("pincode", ""),
        experience_years=data.get("experience_years"),
        bio=data.get("bio", "")
    )

    status_code = 200 if success else 400

    return jsonify({
        "success": success,
        "message": message
    }), status_code


@maid.route("/profile-page")
@role_required("MAID")
def profile_page():
    return render_template("maid/profile.html")