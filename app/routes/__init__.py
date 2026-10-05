from flask import Blueprint, render_template
from app.database import fetch_one


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