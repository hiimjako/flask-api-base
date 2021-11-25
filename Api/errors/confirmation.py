from werkzeug.exceptions import HTTPException
from http import HTTPStatus


class ConfirmationNotFound(HTTPException):
    pass


class ConfirmationExpired(HTTPException):
    pass


class ConfirmationAlreadyConfirmed(HTTPException):
    pass


class ConfirmationCreate(HTTPException):
    pass


errors = {
    "ConfirmationExpired": {
        "message": "The confirmation token has expired.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "ConfirmationAlreadyConfirmed": {
        "message": "The confirmation token has been already confirmed.",
        "status": HTTPStatus.BAD_REQUEST,
    },
    "ConfirmationNotFound": {
        "message": "Confirmation not found.",
        "status": HTTPStatus.NOT_FOUND,
    },
    "ConfirmationCreate": {
        "message": "Internal server error. Failed to create confirmation.",
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
    },
}
