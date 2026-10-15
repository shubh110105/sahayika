
from flask import Blueprint, request, jsonify, session

from app.services.requirement_service import (
    create_household_requirement,
    list_customer_requirements,
)

requirement = Blueprint("requirement", __name__, url_prefix="/requirements")


@requirement.route("/", methods=["POST"])
def create_requirement():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({
            "success": False,
            "message": "Only customers can create household requirements."
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be valid JSON."
        }), 400

    success, result = create_household_requirement(
        customer_id=session["user_id"],
        location_address=data.get("location_address"),
        city=data.get("city"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        experience_requirement=data.get("experience_requirement"),
        additional_requirements=data.get("additional_requirements"),
        service_ids=data.get("service_ids"),
        schedules=data.get("schedules"),
    )

    if not success:
        return jsonify({
            "success": False,
            "message": result
        }), 400

    return jsonify({
        "success": True,
        "message": "Household requirement created successfully.",
        "requirement_id": result
    }), 201


@requirement.route("/", methods=["GET"])
def get_requirements():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({
            "success": False,
            "message": "Only customers can view their requirements."
        }), 403

    requirements = list_customer_requirements(session["user_id"])

    return jsonify({
        "success": True,
        "requirements": requirements
    }), 200
