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


@maid.route("/assignments/<int:assignment_id>/response", methods=["POST"])
@role_required("MAID")
def assignment_response(assignment_id):
    """Allow the assigned maid to accept or reject an assignment."""

    from app.models.assignment_response_model import respond_to_assignment

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    decision = data.get("decision")

    if decision not in {"ACCEPT", "REJECT"}:
        return jsonify({
            "success": False,
            "message": "Decision must be ACCEPT or REJECT."
        }), 400

    maid_id = session.get("user_id")

    if maid_id is None:
        return jsonify({
            "success": False,
            "message": "Maid session is missing. Please log in again."
        }), 401

    try:
        success, message = respond_to_assignment(
            assignment_id=assignment_id,
            maid_id=maid_id,
            decision=decision
        )

        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400

        return jsonify({
            "success": True,
            "message": message,
            "assignment_id": assignment_id,
            "status": (
                "MAID_ACCEPTED"
                if decision == "ACCEPT"
                else "MAID_REJECTED"
            )
        }), 200

    except Exception as error:
        print("MAID ASSIGNMENT RESPONSE ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to save the assignment response."
        }), 500

@maid.route("/verification/submit", methods=["POST"])
@role_required("MAID")
def submit_maid_verification():
    """Allow a maid to submit a verification request."""

    from app.services.verification_service import submit_verification

    maid_user_id = session.get("user_id")

    if maid_user_id is None:
        return jsonify({
            "success": False,
            "message": "Maid session is missing. Please log in again."
        }), 401

    try:
        success, message = submit_verification(maid_user_id)

        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400

        return jsonify({
            "success": True,
            "message": message
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to submit the verification request."
        }), 500

@maid.route("/services", methods=["GET"])
@role_required("MAID")
def get_my_services():
    """Return available services and the logged-in maid's selections."""
    from app.models.maid_service_model import (
        get_all_services,
        get_maid_services
    )

    maid_id = session.get("user_id")

    try:
        return jsonify({
            "success": True,
            "available_services": get_all_services(),
            "my_services": get_maid_services(maid_id)
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to load maid services."
        }), 500


@maid.route("/services", methods=["POST"])
@role_required("MAID")
def save_my_services():
    """Save service selections for the logged-in maid."""
    from app.models.maid_service_model import save_maid_services

    maid_id = session.get("user_id")
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    selected_services = data.get("service_ids")

    if not isinstance(selected_services, list):
        return jsonify({
            "success": False,
            "message": "service_ids must be a list."
        }), 400

    # Reject booleans, strings, zero, and negative service IDs.
    if any(
        isinstance(service_id, bool)
        or not isinstance(service_id, int)
        or service_id <= 0
        for service_id in selected_services
    ):
        return jsonify({
            "success": False,
            "message": "Every service ID must be a positive integer."
        }), 400

    try:
        success, message = save_maid_services(
            maid_id=maid_id,
            selected_services=selected_services
        )

        return jsonify({
            "success": success,
            "message": message
        }), 200 if success else 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to save maid services."
        }), 500

@maid.route("/services/page", methods=["GET"])
@role_required("MAID")
def my_services_page():
    """Render the maid service-management page."""
    return render_template("maid/services.html")

@maid.route("/availability", methods=["GET"])
@role_required("MAID")
def get_my_availability():
    """Return availability slots for the logged-in maid."""
    from app.models.availability_model import get_maid_availability

    maid_id = session.get("user_id")

    try:
        slots = get_maid_availability(maid_id)
        return jsonify({
            "success": True,
            "availability": slots or []
        }), 200
    except Exception:
        import logging
        logging.exception("Failed to load maid availability")
        return jsonify({
            "success": False,
            "message": "Unable to load availability."
        }), 500


@maid.route("/availability", methods=["POST"])
@role_required("MAID")
def add_my_availability():
    """Add an availability slot for the logged-in maid."""
    from app.models.availability_model import add_maid_availability

    maid_id = session.get("user_id")
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    day = data.get("day_of_week")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if (
        not isinstance(day, int)
        or isinstance(day, bool)
        or not isinstance(start_time, str)
        or not isinstance(end_time, str)
    ):
        return jsonify({
            "success": False,
            "message": "Please provide a valid day and time range."
        }), 400

    # Validate the time format before calling the model.
    from datetime import time

    try:
        parsed_start = time.fromisoformat(start_time)
        parsed_end = time.fromisoformat(end_time)
        start_time = parsed_start.strftime("%H:%M:%S")
        end_time = parsed_end.strftime("%H:%M:%S")
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Times must use HH:MM or HH:MM:SS format."
        }), 400

    try:
        success, message = add_maid_availability(
            maid_id, day, start_time, end_time
        )
        return jsonify({
            "success": success,
            "message": message
        }), 201 if success else 400
    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to add availability."
        }), 500


@maid.route("/availability/<int:availability_id>/status", methods=["POST"])
@role_required("MAID")
def change_my_availability_status(availability_id):
    """Activate or deactivate one of the logged-in maid's slots."""
    from app.models.availability_model import (
        update_maid_availability_status
    )

    maid_id = session.get("user_id")
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    status = data.get("status")

    try:
        success, message = update_maid_availability_status(
            maid_id, availability_id, status
        )
        return jsonify({
            "success": success,
            "message": message
        }), 200 if success else 400
    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to update availability."
        }), 500

@maid.route("/availability/page", methods=["GET"])
@role_required("MAID")
def my_availability_page():
    """Render the maid availability management page."""
    return render_template("maid/availability.html")



@maid.route("/assignments", methods=["GET"])
@role_required("MAID")
def get_my_assignments():
    """Return assignments for the logged-in maid."""
    from app.models.maid_assignment_model import get_maid_assignments

    maid_id = session.get("user_id")

    try:
        assignments = get_maid_assignments(maid_id)

        return jsonify({
            "success": True,
            "assignments": assignments or []
        }), 200

    except Exception:
        import logging
        logging.exception("Failed to load maid assignments")

        return jsonify({
            "success": False,
            "message": "Unable to load assignments."
        }), 500

@maid.route("/assignments/page", methods=["GET"])
@role_required("MAID")
def my_assignments_page():
    """Render the maid assignments page."""
    return render_template("maid/assignments.html")


@maid.route("/employments/active", methods=["GET"])
@role_required("MAID")
def maid_active_employments_route():
    """Return active employments belonging to the logged-in maid."""
    from app.models.maid_employment_model import (
        get_maid_active_employments
    )

    maid_id = session.get("user_id")
    employments = get_maid_active_employments(maid_id)

    return jsonify({
        "success": True,
        "employments": employments
    }), 200



@maid.route("/employments/active/page", methods=["GET"])
@role_required("MAID")
def maid_active_employments_page():
    """Render the logged-in maid's active employment page."""
    return render_template("maid/active_employments.html")
