from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class UsernameAlreadyExists(HTTPException):
    pass


class UserEmailAlreadyExists(HTTPException):
    pass


class UserCreate(HTTPException):
    pass


class UserNotFound(HTTPException):
    pass


class UserInvalidCredentials(HTTPException):
    pass


class UserInvalidEmail(HTTPException):
    pass


class UserNotConfirmed(HTTPException):
    pass


class UserHasNoPermission(HTTPException):
    pass


class UserIsNotLoggedIn(HTTPException):
    pass


errors = {
    "UsernameAlreadyExists": {
        "message": "A user with that username already exists.",
        "status": HTTPStatus.CONFLICT,
    },
    "UserEmailAlreadyExists": {
        "message": "A user with that email already exists.",
        "status": HTTPStatus.CONFLICT,
    },
    "UserNotFound": {
        "message": "User not found.",
        "status": HTTPStatus.NOT_FOUND,
    },
    "UserCreate": {
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
    "UserHasNoPermission": {
        "message": "User doesn't have the correct permissions.",
        "status": HTTPStatus.UNAUTHORIZED,
    },
    "UserIsNotLoggedIn": {
        "message": "User isn't logged, log in before.",
        "status": HTTPStatus.UNAUTHORIZED,
    },
}
