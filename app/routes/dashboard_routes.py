from flask import Blueprint, render_template
from app.role_required import role_required


dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/customer/dashboard")
@role_required("CUSTOMER")
def customer_dashboard():
    return render_template("customer/dashboard.html")


@dashboard.route("/maid/dashboard")
@role_required("MAID")
def maid_dashboard():
    return render_template("maid/dashboard.html")


@dashboard.route("/admin/dashboard")
@role_required("ADMIN")
def admin_dashboard():
    return render_template("admin/dashboard.html")

