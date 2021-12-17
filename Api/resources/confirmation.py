import Api.errors.confirmation as ConfirmationException
import Api.errors.user as UserException
from Api.models.user import UserModel
from Api.schemas.common import GenericReturnSchema
from flask import make_response, render_template
from flask_apispec import doc, marshal_with
from flask_apispec.views import MethodResource
from flask_restful import Resource


class Confirmation(MethodResource, Resource):
    @doc(
        description="Confirm the user with confirmation token",
        params={
            "confirmation_token": {
                "description": "The ID of the confirmation",
                "example": "cdb93c441cee49ada0527862b7f73350",
            },
            "bypass-user-id": {
                "description": "Admin user is enabled to bypass a user",
                "in": "query",
                "type": "string",
                "required": False,
            },
        },
        tags=["Confirmation"],
    )
    @marshal_with(GenericReturnSchema)
    def get(self, confirmation_token: str):
        user = UserModel.user_by_token(confirmation_token)
        if not user:
            raise UserException.UserNotFound

        if user.confirmed:
            raise ConfirmationException.ConfirmationAlreadyConfirmed

        # if i get the user here the token is valid
        user.confirmed = True
        user.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html"),
            200,
            headers,
        )
        # Url_for
        # return redirect("www.google.it")
