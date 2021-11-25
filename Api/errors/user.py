from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class UsernameAlreadyExistsError(HTTPException):
    pass


class UserEmailAlreadyExistsError(HTTPException):
    pass


class UserCreateError(HTTPException):
    pass


class UserNotFound(HTTPException):
    pass


class UserInvalidCredentials(HTTPException):
    pass


class UserInvalidEmail(HTTPException):
    pass


class UserNotConfirmed(HTTPException):
    pass


errors = {
    "UsernameAlreadyExistsError": {
        "message": "A user with that username already exists.",
        "status": HTTPStatus.CONFLICT,
    },
    "UserEmailAlreadyExistsError": {
        "message": "A user with that email already exists.",
        "status": HTTPStatus.CONFLICT,
    },
    "UserNotFound": {
        "message": "User not found.",
        "status": HTTPStatus.NOT_FOUND,
    },
    "UserCreateError": {
        "message": "Internal server error. Failed to create user.",
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
    },
    "UserInvalidCredentials": {
        "message": "User credentials invalid.",
        "status": HTTPStatus.UNAUTHORIZED,
    },
    "UserNotConfirmed": {
        "message": "User not yet confirmed.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "UserInvalidEmail": {
        "message": "Email is not valid.",
        "status": HTTPStatus.BAD_REQUEST,
    },
}
