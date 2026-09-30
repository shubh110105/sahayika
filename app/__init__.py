from flask import Flask
from app.config import Config
from app.routes import main
from app.routes.auth_routes import auth


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app