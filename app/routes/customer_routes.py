from flask import Blueprint, request, jsonify, session, render_template

from app.role_required import role_required
from app.services.customer_service import (
    get_customer_profile,
    save_customer_profile
)


customer = Blueprint(
    "customer",
    __name__,
    url_prefix="/customer"
)


@customer.route("/profile", methods=["GET"])
@role_required("CUSTOMER")
def get_profile():
    user_id = session["user_id"]

    profile = get_customer_profile(user_id)

    if not profile:
        return jsonify({
            "success": False,
            "message": "Customer not found."
        }), 404

    return jsonify({
        "success": True,
        "profile": profile
    })


@customer.route("/profile", methods=["POST"])
@role_required("CUSTOMER")
def save_profile():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    user_id = session["user_id"]

    success, message = save_customer_profile(
        customer_id=user_id,
        address=data.get("address", ""),
        city=data.get("city", ""),
        state=data.get("state", ""),
        pincode=data.get("pincode", "")
    )

    status_code = 200 if success else 400

    return jsonify({
        "success": success,
        "message": message
    }), status_code

@customer.route("/profile-page")
@role_required("CUSTOMER")
def profile_page():
    return render_template("customer/profile.html")