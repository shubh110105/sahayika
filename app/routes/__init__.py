from flask import Blueprint, abort, current_app, render_template, session

from app.database import fetch_one
from app.role_required import role_required


main = Blueprint("main", __name__)


def _debug_only():
    """Diagnostic endpoints exist for local development only."""
    if not current_app.debug:
        abort(404)


@main.route("/db-test")
def db_test():
    _debug_only()

    result = fetch_one(
        "SELECT COUNT(*) AS service_count FROM services"
    )

    return (
        f"Database connected successfully. "
        f"Services: {result['service_count']}"
    )


@main.route("/register")
def register_page():
    return render_template("register.html")


@main.route("/login")
def login_page():
    return render_template("login.html")


@main.route("/customer-test")
@role_required("CUSTOMER")
def customer_test():
    _debug_only()
    return "Customer access granted."


@main.route("/maid-test")
@role_required("MAID")
def maid_test():
    _debug_only()
    return "Maid access granted."


@main.route("/admin-test")
@role_required("ADMIN")
def admin_test():
    _debug_only()
    return "Admin access granted."


@main.route("/session-test")
def session_test():
    _debug_only()

    return {
        "logged_in": "user_id" in session,
        "user_id": session.get("user_id"),
        "role": session.get("role")
    }
