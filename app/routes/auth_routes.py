from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    success, result = register_user(
        full_name=data.get("full_name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        password=data.get("password", ""),
        role=data.get("role", "")
    )

    if not success:
        return jsonify({
            "success": False,
            "message": result
        }), 400

    return jsonify({
        "success": True,
        "message": "Account created successfully.",
        "user_id": result
    }), 201