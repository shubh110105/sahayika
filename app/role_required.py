from functools import wraps

from flask import jsonify, redirect, render_template_string, request, session


FORBIDDEN_PAGE = (
    "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
    "<title>Access denied</title></head><body style='font-family:sans-serif;"
    "margin:3rem'><h2>Access denied</h2><p>You do not have permission to "
    "view this page.</p><p><a href='/'>Go back</a></p></body></html>"
)


def _wants_html_page():
    """True for a normal browser page visit, False for fetch()/API calls."""
    return request.accept_mimetypes.best == "text/html"


def role_required(*allowed_roles):
    def decorator(view_function):

        @wraps(view_function)
        def wrapped_view(*args, **kwargs):

            user_id = session.get("user_id")
            user_role = session.get("role")

            if not user_id:
                # Browsers opening a page get sent to the login form;
                # JavaScript API calls still receive JSON.
                if _wants_html_page():
                    return redirect("/login")

                return jsonify({
                    "success": False,
                    "message": "Login required."
                }), 401

            if user_role not in allowed_roles:
                if _wants_html_page():
                    return render_template_string(FORBIDDEN_PAGE), 403

                return jsonify({
                    "success": False,
                    "message": "Access denied."
                }), 403

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator
