import traceback
from http import HTTPStatus
from time import time

from flask_apispec.views import MethodResource
from flask_jwt_extended.view_decorators import jwt_required
from Api.decorators import doc_with_jwt
import Api.errors.confirmation as ConfirmationException
import Api.errors.user as UserException


from Api.libs.strings import gettext
from Api.models.confirmation import ConfirmationModel
from Api.models.user import UserModel
from Api.schemas.common import GenericReturnSchema
from Api.schemas.confirmation import ConfirmationSchema
from flask import make_response, redirect, render_template
from flask_apispec import doc, marshal_with
from flask_restful import Resource

confirmation_schema = ConfirmationSchema()


class Confirmation(MethodResource, Resource):
    @doc(
        description="Confirm the user with confirmation token",
        params={
            "confirmation_id": {
                "description": "The ID of the confirmation",
                "example": "cdb93c441cee49ada0527862b7f73350",
            }
        },
        tags=["Confirmation"],
    )
    def get(self, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            raise ConfirmationException.ConfirmationNotFound

        if confirmation.expired:
            raise ConfirmationException.ConfirmationExpired

        if confirmation.confirmed:
            raise ConfirmationException.ConfirmationAlreadyConfirmed

        confirmation.confirmed = True
        confirmation.save_to_db()

        # headers = {"Content-Type": "text/html"}
        # return make_response(
        #     render_template("confirmation_page.html", email=confirmation.user.email),
        #     200,
        #     headers,
        # )
        # Url_for
        return redirect("www.google.it")


class ConfirmationByUser(MethodResource, Resource):
    @doc_with_jwt(
        description="""This endpoint resend the confirmation email with a new confirmation model. It will force the current 
        confirmation model to expire so that there is only one valid link at once.""",
        params={
            "user_id": {
                "description": "The ID of the user",
                "example": "12",
            }
        },
        tags=["Confirmation"],
    )
    @marshal_with(GenericReturnSchema)
    @jwt_required()
    def post(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        try:
            # find the most current confirmation for the user
            confirmation = user.most_recent_confirmation  # using property decorator
            if confirmation:
                if confirmation.confirmed:
                    raise ConfirmationException.ConfirmationAlreadyConfirmed
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)  # create a new confirmation
            new_confirmation.save_to_db()
            # Does `user` object know the new confirmation by now? Yes.
            # An excellent example where lazy='dynamic' comes into use.
            user.send_confirmation_email()  # re-send the confirmation email
            return {
                "message": gettext("confirmation_resend_successful")
            }, HTTPStatus.CREATED
        except:
            traceback.print_exc()
            raise ConfirmationException.ConfirmationCreate
