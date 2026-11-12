import os

from app import create_app


app = create_app()


if __name__ == "__main__":
    # Debug mode exposes an interactive debugger, so it is opt-in only.
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
