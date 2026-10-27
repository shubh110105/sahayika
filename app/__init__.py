"""from flask import Flask  #Import the Flask class from the Flask package.
from app.config import Config
from app.routes import main
from app.routes.auth_routes import auth


def create_app():  #Create a function called create_app that will create our Flask application.
    app = Flask(__name__)

    app.config.from_object(Config) #Flask has a built-in place called config where we can store application settings.#Take the settings from the Config class and put them into this Flask application's configuration.


    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
"""
from flask import Flask
from app.config import Config
from app.routes import main
from app.routes.auth_routes import auth
from app.routes.dashboard_routes import dashboard
from app.routes.customer_routes import customer
from app.routes.maid_routes import maid
from app.routes.verification_routes import verification
from app.routes.requirement_routes import requirement
from app.routes.admin_routes import admin

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(customer)
    app.register_blueprint(maid)
    app.register_blueprint(verification)
    app.register_blueprint(requirement)
    app.register_blueprint(admin)

    return app