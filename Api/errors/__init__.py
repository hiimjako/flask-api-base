from Api.errors.user import errors as user_errors
from Api.errors.confirmation import errors as confirmation_errors

errors = {**user_errors, **confirmation_errors}
