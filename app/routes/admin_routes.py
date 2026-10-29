
from flask import Blueprint, jsonify, render_template, request, session
from app.role_required import role_required

from app.models.requirement_model import (
    get_salary_review_requests,
    update_salary_review_decision,
    reset_failed_salary_reassessment, # Restore failed reassessments to the queue.
       get_submitted_requirements_for_admin, 
)

# Import the service that recalculates and saves an estimate.
from app.services.requirement_service import reassess_requirement_salary

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/salary-reviews", methods=["GET"])
@role_required("ADMIN")
def salary_review_requests():
    try:
        requests = get_salary_review_requests()

        return jsonify({
            "success": True,
            "requests": requests
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to load salary review requests."
        }), 500

@admin.route("/salary-reviews/page", methods=["GET"])
@role_required("ADMIN")
def salary_review_page():
    return render_template("admin/salary_reviews.html")


@admin.route(
    "/salary-reviews/<int:requirement_id>/decision",
    methods=["POST"]
)
@role_required("ADMIN")
def submit_salary_review_decision(requirement_id):
    from flask import request

    # Read the decision submitted by the Admin interface.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    decision = data.get("decision")

    # Accept only the two supported Admin decisions.
    if decision not in {"APPROVED", "REASSESSMENT_REQUESTED"}:
        return jsonify({
            "success": False,
            "message": "Invalid salary review decision."
        }), 400

    try:
        # Save the Admin's decision before performing further work.
        updated = update_salary_review_decision(
            requirement_id,
            decision
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": (
                    "This review could not be updated. "
                    "It may already have been resolved or may not exist."
                )
            }), 400

        # If reassessment was requested, recalculate the salary now.
        if decision == "REASSESSMENT_REQUESTED":
            success, result = reassess_requirement_salary(requirement_id)

            
            if not success:
                # Reset the decision so the Admin can retry the failed reassessment.
                reset_failed_salary_reassessment(requirement_id)

                # Report the failure instead of claiming the reassessment worked.
                return jsonify({
                    "success": False,
                    "message": (
                        f"{result} The request has been returned to the pending queue "
                        "so you can try again."
                    )
                }), 500

            return jsonify({
                "success": True,
                "message": "Salary reassessed successfully.",
                "estimated_monthly_salary": (
                    result["estimated_monthly_salary"]
                )
            }), 200

        # Approval keeps the existing behavior: save the decision and respond.
        return jsonify({
            "success": True,
            "message": "Salary estimate approved successfully."
        }), 200

    except Exception:
        # Avoid exposing internal database or application errors to the client.
        return jsonify({
            "success": False,
            "message": "Unable to process the salary review decision."
        }), 500



@admin.route(
    "/requirements/<int:requirement_id>/shortlist",
    methods=["GET"]
)
@role_required("ADMIN")
def requirement_maid_shortlist(requirement_id):
    """Show eligible maid recommendations; this endpoint does not assign a maid."""
    from app.models.matching_model import get_maid_shortlist

    try:
        requirement, candidates, message = get_maid_shortlist(requirement_id)

        if requirement is None:
            return jsonify({
                "success": False,
                "message": message,
                "candidates": []
            }), 404

        return jsonify({
            "success": True,
            "requirement_id": requirement_id,
            "requirement_status": requirement["status"],
            "message": message,
            "candidates": candidates
        }), 200

    except Exception:
        # Keep internal SQL details out of the API response.
        return jsonify({
            "success": False,
            "message": "Unable to generate the maid shortlist."
        }), 500



@admin.route("/requirements", methods=["GET"])
@role_required("ADMIN")
def submitted_requirements():
    """List household requirements awaiting Admin review."""
    try:
        requirements = get_submitted_requirements_for_admin()

        return jsonify({
            "success": True,
            "requirements": requirements or []
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to load submitted requirements."
        }), 500

@admin.route(
    "/requirements/<int:requirement_id>/assign",
    methods=["POST"]
)
@role_required("ADMIN")
def assign_maid_to_requirement(requirement_id):
    """Let an Admin manually select an eligible maid."""

    from app.models.assignment_model import create_maid_assignment

    # Read the selected maid ID from the JSON request body.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    maid_id = data.get("maid_id")

    # Validate the maid ID before passing it to the model.
    if (
        isinstance(maid_id, bool)
        or not isinstance(maid_id, int)
        or maid_id <= 0
    ):
        return jsonify({
            "success": False,
            "message": "A valid positive maid_id is required."
        }), 400

    # Get the logged-in Admin's user ID from the session.
    admin_id = session.get("user_id")

    if admin_id is None:
        return jsonify({
            "success": False,
            "message": "Admin session is missing. Please log in again."
        }), 401

    try:
        success, message, assignment_id = create_maid_assignment(
            requirement_id=requirement_id,
            maid_id=maid_id,
            admin_id=admin_id
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
            "status": "PENDING_MAID_RESPONSE"
        }), 201

    except Exception as error:
        print("ASSIGNMENT CREATION ERROR:", repr(error))

        # Keep internal details out of the API response.
        return jsonify({
            "success": False,
            "message": "Unable to create the assignment."
        }), 500


    
@admin.route(
    "/assignments/<int:assignment_id>/confirm",
    methods=["POST"]
)
@role_required("ADMIN")
def finalize_assignment_route(assignment_id):
    """Give final Admin confirmation and activate employment."""

    from app.models.employment_model import finalize_assignment

    admin_id = session.get("user_id")

    if admin_id is None:
        return jsonify({
            "success": False,
            "message": "Admin session is missing. Please log in again."
        }), 401

    try:
        success, message, employment_id = finalize_assignment(
            assignment_id=assignment_id,
            admin_id=admin_id
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
            "assignment_status": "ADMIN_CONFIRMED",
            "employment_id": employment_id,
            "employment_status": "ACTIVE"
        }), 200

    except Exception as error:
        print("FINAL ADMIN CONFIRMATION ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to finalize the assignment."
        }), 500

@admin.route(
    "/requirements/<int:requirement_id>/shortlist/page",
    methods=["GET"]
)
@role_required("ADMIN")
def requirement_maid_shortlist_page(requirement_id):
    """Render the Admin page for reviewing and assigning shortlisted maids."""
    return render_template(
        "admin/maid_shortlist.html",
        requirement_id=requirement_id
    )

@admin.route("/verifications", methods=["GET"])
@role_required("ADMIN")
def pending_maid_verifications():
    """Return maid verification requests awaiting Admin review."""
    from app.services.verification_service import list_pending_verifications

    try:
        verifications = list_pending_verifications()

        return jsonify({
            "success": True,
            "verifications": verifications or []
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to load pending maid verifications."
        }), 500


@admin.route(
    "/verifications/<int:verification_id>/decision",
    methods=["POST"]
)
@role_required("ADMIN")
def review_maid_verification(verification_id):
    """Allow an Admin to verify, reject, or suspend a pending request."""
    from app.services.verification_service import review_verification

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    decision = data.get("decision")
    remarks = data.get("remarks", "")

    if decision not in {"VERIFIED", "REJECTED", "SUSPENDED"}:
        return jsonify({
            "success": False,
            "message": "Invalid verification decision."
        }), 400

    admin_id = session.get("user_id")

    if admin_id is None:
        return jsonify({
            "success": False,
            "message": "Admin session is missing. Please log in again."
        }), 401

    try:
        success, message = review_verification(
            verification_id=verification_id,
            status=decision,
            remarks=remarks,
            admin_user_id=admin_id
        )

        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400

        return jsonify({
            "success": True,
            "message": message,
            "verification_id": verification_id,
            "status": decision
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to process the verification decision."
        }), 500

@admin.route("/verifications/page", methods=["GET"])
@role_required("ADMIN")
def pending_maid_verifications_page():
    """Render the Admin verification queue page."""
    return render_template("admin/maid_verifications.html")



@admin.route("/assignments/pending-confirmation", methods=["GET"])
@role_required("ADMIN")
def pending_admin_assignments():
    """List assignments awaiting final Admin confirmation."""
    from app.models.admin_assignment_model import (
        get_assignments_pending_admin_confirmation
    )

    try:
        assignments = get_assignments_pending_admin_confirmation()

        return jsonify({
            "success": True,
            "assignments": assignments or []
        }), 200

    except Exception:
        import logging
        logging.exception(
            "Failed to load assignments awaiting Admin confirmation"
        )

        return jsonify({
            "success": False,
            "message": "Unable to load assignments awaiting confirmation."
        }), 500

@admin.route("/assignments/page", methods=["GET"])
@role_required("ADMIN")
def admin_assignments_page():
    """Render the Admin assignment review page."""
    return render_template("admin/assignments.html")


@admin.route("/employments/active", methods=["GET"])
@role_required("ADMIN")
def active_employments_route():
    """Return active employment records for Admin review."""
    from app.models.active_employment_model import get_active_employments

    employments = get_active_employments()

    return jsonify({
        "success": True,
        "employments": employments
    }), 200


@admin.route("/employments/active/page", methods=["GET"])
@role_required("ADMIN")
def active_employments_page():
    """Render the Admin Active Employments page."""
    return render_template("admin/active_employments.html")



@admin.route("/attendance/disputes", methods=["GET"])
@role_required("ADMIN")
def admin_attendance_disputes_route():
    """Return attendance disputes for Admin review."""

    from app.models.admin_attendance_dispute_model import (
        get_all_attendance_disputes
    )

    disputes = get_all_attendance_disputes()

    return jsonify({
        "success": True,
        "disputes": disputes
    }), 200



@admin.route("/attendance/disputes/page", methods=["GET"])
@role_required("ADMIN")
def admin_attendance_disputes_page():
    """Render the Admin attendance disputes page."""
    return render_template("admin/attendance_disputes.html")




@admin.route(
    "/attendance/disputes/<int:dispute_id>/decide",
    methods=["POST"]
)
@role_required("ADMIN")
def admin_decide_attendance_dispute_route(dispute_id):
    """Resolve or reject an attendance dispute."""

    from flask import request
    from app.models.admin_attendance_dispute_model import (
        decide_attendance_dispute
    )

    admin_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    decision = data.get("decision")
    reason = data.get("reason")
    attendance_outcome = data.get("attendance_outcome")

    success, message = decide_attendance_dispute(
        admin_id=admin_id,
        dispute_id=dispute_id,
        decision=decision,
        reason=reason,
        attendance_outcome=attendance_outcome
    )

    return jsonify({
        "success": success,
        "message": message
    }), 200 if success else 400

