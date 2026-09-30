from flask import Blueprint
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