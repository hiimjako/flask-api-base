import traceback
from http import HTTPStatus
from time import time

from Api.libs.strings import gettext
from Api.models.confirmation import ConfirmationModel
from Api.models.user import UserModel
from Api.schemas.confirmation import ConfirmationSchema
from flask import make_response, redirect, render_template
from flask_restful import Resource

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    # returns the confirmation page
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, HTTPStatus.NOT_FOUND

        if confirmation.expired:
            return {
                "message": gettext("confirmation_link_expired")
            }, HTTPStatus.BAD_REQUEST

        if confirmation.confirmed:
            return {
                "message": gettext("confirmation_already_confirmed")
            }, HTTPStatus.BAD_REQUEST

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


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        This endpoint is used for testing and viewing Confirmation models and should not be exposed to public.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND
        return (
            {
                "current_time": int(time()),
                # we filter the result by expiration time in descending order for convenience
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            HTTPStatus.OK,
        )

    @classmethod
    def post(cls, user_id):
        """
        This endpoint resend the confirmation email with a new confirmation model. It will force the current
        confirmation model to expire so that there is only one valid link at once.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, HTTPStatus.NOT_FOUND

        try:
            # find the most current confirmation for the user
            confirmation = user.most_recent_confirmation  # using property decorator
            if confirmation:
                if confirmation.confirmed:
                    return {
                        "message": gettext("confirmation_already_confirmed")
                    }, HTTPStatus.BAD_REQUEST
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
            return {
                "message": gettext("confirmation_resend_fail")
            }, HTTPStatus.INTERNAL_SERVER_ERROR
