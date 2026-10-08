from flask import Blueprint, render_template
from app.database import fetch_one
from app.role_required import role_required
from flask import session

main = Blueprint("main", __name__)


@main.route("/db-test")
def db_test():
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
    return "Customer access granted."


@main.route("/maid-test")
@role_required("MAID")
def maid_test():
    return "Maid access granted."


@main.route("/admin-test")
@role_required("ADMIN")
def admin_test():
    return "Admin access granted."

@main.route("/session-test")
def session_test():
    return {
        "logged_in": "user_id" in session,
        "user_id": session.get("user_id"),
        "role": session.get("role")
    }