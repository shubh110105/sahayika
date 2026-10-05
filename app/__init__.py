from flask import Flask  #Import the Flask class from the Flask package.
from app.config import Config
from app.routes import main
from app.routes.auth_routes import auth


def create_app():  #Create a function called create_app that will create our Flask application.
    app = Flask(__name__)

    app.config.from_object(Config) #Flask has a built-in place called config where we can store application settings.#Take the settings from the Config class and put them into this Flask application's configuration.


    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app