from flask_apispec.annotations import activate, annotate


def doc_with_jwt(inherit=None, **kwargs):
    def wrapper(func):
        if not "params" in kwargs:
            kwargs["params"] = {}
        if not "Authorization" in kwargs["params"]:
            kwargs["params"]["Authorization"] = {
                "description": "Authorization HTTP header with JWT access token, like: Authorization: Bearer <token>",
                "in": "header",
                "type": "string",
                "required": True,
            }
        annotate(func, "docs", [kwargs], inherit=inherit)
        return activate(func)

    return wrapper
