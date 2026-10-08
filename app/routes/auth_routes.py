from flask import Blueprint, request, jsonify, session
from app.services.auth_service import register_user
from app.models.user_model import get_user_by_email
from app.auth_utils import verify_password


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


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    user = get_user_by_email(email)

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if not verify_password(password, user["password_hash"]):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if user["status"] != "ACTIVE":
        return jsonify({
            "success": False,
            "message": "This account is not active."
        }), 403

    session.clear()

    session["user_id"] = user["user_id"]
    session["role"] = user["role"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user_id": user["user_id"],
        "role": user["role"]
    })

@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })