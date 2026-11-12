from flask import Flask, redirect, render_template, session, url_for

from app.config import Config
from app.routes import main
from app.routes.auth_routes import auth
from app.routes.dashboard_routes import dashboard
from app.routes.customer_routes import customer
from app.routes.maid_routes import maid
from app.routes.verification_routes import verification
from app.routes.requirement_routes import requirement
from app.routes.admin_routes import admin


DASHBOARD_ENDPOINTS = {
    "CUSTOMER": "dashboard.customer_dashboard",
    "MAID": "dashboard.maid_dashboard",
    "ADMIN": "dashboard.admin_dashboard",
}


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Without a secret key Flask cannot sign sessions, so logins would
    # fail with a confusing error. Fail early with a clear message.
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(customer)
    app.register_blueprint(maid)
    app.register_blueprint(verification)
    app.register_blueprint(requirement)
    app.register_blueprint(admin)

    @app.route("/")
    def index():
        """
        Show the landing page to visitors.
        Redirect authenticated users to their respective dashboards.
        """

        endpoint = DASHBOARD_ENDPOINTS.get(session.get("role"))

        if session.get("user_id") and endpoint:
            return redirect(url_for(endpoint))

        return render_template("landing.html")
    @app.context_processor
    def inject_app_name():
        return {"app_name": app.config["APP_NAME"]}

    @app.after_request
    def disable_caching_for_signed_in_pages(response):
        # Stops the browser "Back" button from showing a cached dashboard
        # after logout.
        if session.get("user_id") and response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store"

        return response

    return app
