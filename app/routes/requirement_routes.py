
from flask import Blueprint, request, jsonify, session, render_template

from app.role_required import role_required
from app.services.requirement_service import (
    create_household_requirement,
    list_customer_requirements,
)


from app.models.requirement_model import (
    get_all_services,
    get_requirement_by_id,
    get_requirement_services,
    get_requirement_schedules,
    request_salary_review,
    cancel_household_requirement,
    submit_requirement_for_matching,
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

@requirement.route("/new", methods=["GET"])
def requirement_page():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({
            "success": False,
            "message": "Only customers can access this page."
        }), 403

    services = get_all_services()

    return render_template(
        "customer/requirement_form.html",
        services=services
    )

@requirement.route("/my", methods=["GET"])
def my_requirements_page():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({
            "success": False,
            "message": "Only customers can access this page."
        }), 403

    return render_template("customer/my_requirements.html")


@requirement.route("/<int:requirement_id>", methods=["GET"])
def requirement_details_page(requirement_id):
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if session.get("role") != "CUSTOMER":
        return jsonify({
            "success": False,
            "message": "Only customers can view requirement details."
        }), 403

    requirement_data = get_requirement_by_id(
        requirement_id,
        session["user_id"]
    )

    if not requirement_data:
        return jsonify({
            "success": False,
            "message": "Requirement not found."
        }), 404

    services = get_requirement_services(requirement_id)
    schedules = get_requirement_schedules(requirement_id)

    return render_template(
        "customer/requirement_details.html",
        requirement=requirement_data,
        services=services,
        schedules=schedules
    )

@requirement.route(
    "/<int:requirement_id>/salary-review",
    methods=["POST"]
)
@role_required("CUSTOMER")
def submit_salary_review_request(requirement_id):
    customer_id = session["user_id"]

    try:
        updated = request_salary_review(
            requirement_id,
            customer_id
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": (
                    "Salary review cannot be requested. "
                    "The requirement may not exist, may not belong "
                    "to you, or may not be eligible for review."
                )
            }), 400

        return jsonify({
            "success": True,
            "message": "Salary review request submitted successfully."
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to submit the salary review request."
        }), 500


@requirement.route(
    "/<int:requirement_id>/cancel",
    methods=["POST"]
)
@role_required("CUSTOMER")
def cancel_requirement(requirement_id):
    customer_id = session["user_id"]

    try:
        cancelled = cancel_household_requirement(
            requirement_id,
            customer_id
        )

        if not cancelled:
            return jsonify({
                "success": False,
                "message": (
                    "This requirement cannot be cancelled. "
                    "It may not belong to you or its current status "
                    "may not allow cancellation."
                )
            }), 400

        return jsonify({
            "success": True,
            "message": "Requirement cancelled successfully."
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to cancel the requirement."
        }), 500



@requirement.route(
    "/<int:requirement_id>/submit",
    methods=["POST"]
)
@role_required("CUSTOMER")
def submit_requirement(requirement_id):
    """Let the owning customer accept the estimate and submit the requirement."""
    customer_id = session["user_id"]

    try:
        submitted = submit_requirement_for_matching(
            requirement_id,
            customer_id
        )

        if not submitted:
            return jsonify({
                "success": False,
                "message": (
                    "This requirement cannot be submitted. Confirm that it belongs "
                    "to you, has a saved salary estimate, and is still SALARY_ESTIMATED."
                )
            }), 400

        return jsonify({
            "success": True,
            "message": "Requirement submitted for Admin review."
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to submit the requirement."
        }), 500
