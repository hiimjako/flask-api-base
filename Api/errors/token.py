from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class NotFound(HTTPException):
    pass


class Expired(HTTPException):
    pass


class BadSignature(HTTPException):
    pass


class InvalidUser(HTTPException):
    pass


class AlreadyConfirmed(HTTPException):
    pass


class AlreadyUsed(HTTPException):
    pass


class Create(HTTPException):
    pass


errors = {
    "Expired": {
        "message": "The token has expired.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "BadSignature": {
        "message": "The token is invalid.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "InvalidUser": {
        "message": "The token is invalid.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "AlreadyConfirmed": {
        "message": "The user has been already confirmed.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "NotFound": {
        "message": "Token not found.",
        "status": HTTPStatus.NOT_FOUND,
    },
    "Create": {
        "message": "Internal server error. Failed to create.",
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
    },
    "AlreadyUsed": {
        "message": "The token has been already used.",
        "status": HTTPStatus.BAD_REQUEST,
    },
}
