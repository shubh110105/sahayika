from functools import wraps

from flask import session, jsonify


def role_required(*allowed_roles):
    def decorator(view_function):

        @wraps(view_function)
        def wrapped_view(*args, **kwargs):

            user_id = session.get("user_id")
            user_role = session.get("role")

            if not user_id:
                return jsonify({
                    "success": False,
                    "message": "Login required."
                }), 401

            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "Access denied."
                }), 403

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator