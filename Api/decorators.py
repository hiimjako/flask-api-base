from functools import wraps

from flask_apispec.annotations import activate, annotate

import Api.errors.user as UserException
from Api.jwt import get_current_user_wrapper
from Api.models.permission import Permission


def doc_with_jwt(inherit=None, **kwargs):
    def wrapper(func):
        auth = {
            "description": "Authorization HTTP header with JWT access token, like: Authorization: Bearer <token>",
            "in": "header",
            "type": "string",
            "required": True,
        }
        inc_args = {}
        if not "params" in kwargs:
            kwargs["params"] = {}
        if "Authorization" in kwargs["params"]:
            inc_args = kwargs["params"]["Authorization"]

        kwargs["params"]["Authorization"] = auth
        kwargs["params"]["Authorization"].update(inc_args)
        annotate(func, "docs", [kwargs], inherit=inherit)
        return activate(func)

    return wrapper


def permission_required(permission):
    """Check if the current user has the requested permissions"""

    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            user = get_current_user_wrapper()
            if user is None or not user.can(permission):
                raise UserException.UserHasNoPermission
            return func(*args, **kwargs)

        return decorated_function

    return wrapper


def admin_required(func):
    """Check if the current user is admin"""
    return permission_required(Permission.ADMINISTER)(func)
