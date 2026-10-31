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


@customer.route(
    "/assignments/<int:assignment_id>/confirm",
    methods=["POST"]
)
@role_required("CUSTOMER")
def confirm_assignment(assignment_id):
    """Allow the requirement-owning customer to confirm an accepted assignment."""

    from app.models.customer_assignment_model import confirm_maid_assignment

    customer_id = session.get("user_id")

    if customer_id is None:
        return jsonify({
            "success": False,
            "message": "Customer session is missing. Please log in again."
        }), 401

    try:
        success, message = confirm_maid_assignment(
            assignment_id=assignment_id,
            customer_id=customer_id
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
            "status": "CUSTOMER_CONFIRMED"
        }), 200

    except Exception as error:
        print("CUSTOMER ASSIGNMENT CONFIRMATION ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to confirm the assignment."
        }), 500

@customer.route("/assignments", methods=["GET"])
@role_required("CUSTOMER")
def get_my_assignments():
    """Return assignments belonging to the logged-in customer."""
    from app.models.customer_assignment_list_model import (
        get_customer_assignments
    )

    customer_id = session.get("user_id")

    try:
        assignments = get_customer_assignments(customer_id)

        return jsonify({
            "success": True,
            "assignments": assignments or []
        }), 200

    except Exception:
        import logging
        logging.exception("Failed to load customer assignments")

        return jsonify({
            "success": False,
            "message": "Unable to load assignments."
        }), 500

@customer.route("/assignments/page", methods=["GET"])
@role_required("CUSTOMER")
def my_assignments_page():
    """Render the customer assignments page."""
    return render_template("customer/assignments.html")


@customer.route("/employments/active", methods=["GET"])
@role_required("CUSTOMER")
def customer_active_employments_route():
    """Return active employments belonging to the logged-in customer."""
    from app.models.customer_employment_model import (
        get_customer_active_employments
    )

    customer_id = session.get("user_id")
    employments = get_customer_active_employments(customer_id)

    return jsonify({
        "success": True,
        "employments": employments
    }), 200


@customer.route("/employments/active/page", methods=["GET"])
@role_required("CUSTOMER")
def customer_active_employments_page():
    """Render the customer's active employment page."""
    return render_template("customer/active_employments.html")



@customer.route("/attendance", methods=["GET"])
@role_required("CUSTOMER")
def customer_attendance_route():
    """Return attendance records for the logged-in customer."""
    from app.models.customer_attendance_model import (
        get_customer_attendance
    )

    customer_id = session.get("user_id")
    records = get_customer_attendance(customer_id)

    return jsonify({
        "success": True,
        "attendance": records
    }), 200



@customer.route("/attendance/<int:attendance_id>/review", methods=["POST"])
@role_required("CUSTOMER")
def review_customer_attendance_route(attendance_id):
    """Allow a customer to confirm or dispute attendance."""

    from app.models.customer_attendance_model import (
        confirm_customer_attendance
    )

    data = request.get_json(silent=True) or {}

    decision = data.get("decision")
    reason = data.get("reason")

    customer_id = session.get("user_id")

    success, message = confirm_customer_attendance(
        customer_id=customer_id,
        attendance_id=attendance_id,
        decision=decision,
        reason=reason
    )

    return jsonify({
        "success": success,
        "message": message
    }), (200 if success else 400)


@customer.route("/attendance/page", methods=["GET"])
@role_required("CUSTOMER")
def customer_attendance_page():
    """Render the customer attendance review page."""
    return render_template("customer/attendance.html")


@customer.route("/attendance/disputes/page", methods=["GET"])
@role_required("CUSTOMER")
def customer_attendance_disputes_page():
    """Render the customer attendance disputes page."""
    return render_template("customer/attendance_disputes.html")


@customer.route("/attendance/disputes", methods=["GET"])
@role_required("CUSTOMER")
def customer_attendance_disputes_route():
    """Return attendance disputes for the logged-in customer."""

    from app.models.customer_attendance_model import (
        get_customer_attendance_disputes
    )

    customer_id = session.get("user_id")
    disputes = get_customer_attendance_disputes(customer_id)

    return jsonify({
        "success": True,
        "disputes": disputes
    }), 200


@customer.route("/salary", methods=["GET"])
@role_required("CUSTOMER")
def customer_salary_route():
    """Return finalized salary records for the logged-in customer."""

    from app.models.customer_salary_model import (
        get_customer_salary_records
    )

    customer_id = session.get("user_id")

    try:
        salary_records = get_customer_salary_records(customer_id)

        return jsonify({
            "success": True,
            "salary_records": salary_records or []
        }), 200

    except Exception:
        import logging
        logging.exception("Failed to load customer salary records")

        return jsonify({
            "success": False,
            "message": "Unable to load salary records."
        }), 500

@customer.route("/salary/page", methods=["GET"])
@role_required("CUSTOMER")
def customer_salary_page():
    """Render the customer's salary history page."""
    return render_template("customer/salary.html")