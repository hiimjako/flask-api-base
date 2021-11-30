import Api.errors.confirmation as ConfirmationException
import Api.errors.user as UserException
from Api.models.user import UserModel
from flask import make_response, redirect, render_template
from flask_apispec import doc, marshal_with
from flask_apispec.views import MethodResource
from flask_restful import Resource

from Api.schemas.common import GenericReturnSchema


class Confirmation(MethodResource, Resource):
    @doc(
        description="Confirm the user with confirmation token",
        params={
            "user_id": {
                "description": "The ID of the user",
                "example": "1",
            },
            "confirmation_token": {
                "description": "The ID of the confirmation",
                "example": "cdb93c441cee49ada0527862b7f73350",
            },
        },
        tags=["Confirmation"],
    )
    @marshal_with(GenericReturnSchema)
    def get(self, user_id: int, confirmation_token: str):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        if user.confirmed:
            raise ConfirmationException.ConfirmationAlreadyConfirmed

        if user.is_valid_token(confirmation_token):
            user.confirmed = True
            user.save_to_db()

        # headers = {"Content-Type": "text/html"}
        # return make_response(
        #     render_template("confirmation_page.html", email=confirmation.user.email),
        #     200,
        #     headers,
        # )
        # Url_for
        return redirect("www.google.it")
