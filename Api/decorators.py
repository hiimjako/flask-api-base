from flask_apispec.annotations import activate, annotate


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
