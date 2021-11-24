import traceback
from http import HTTPStatus

import Api.errors.user as UserException
from Api.blocklist import BLOCKLIST
from Api.libs.strings import gettext
from Api.models.confirmation import ConfirmationModel
from Api.models.user import UserModel
from Api.schemas.user import UserSchema
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource
from werkzeug.security import safe_str_cmp

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            raise UserException.UsernameAlreadyExistsError

        if UserModel.find_by_email(user.email):
            raise UserException.UserEmailAlreadyExistsError

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, HTTPStatus.CREATED
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback
            raise UserException.UserCreateError


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        return user_schema.dump(user), HTTPStatus.OK

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        user.delete_from_db()
        return {"message": gettext("user_deleted")}, HTTPStatus.OK


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    HTTPStatus.OK,
                )
            raise UserException.UserNotConfirmed
        raise UserException.UserInvalidCredentials


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLOCKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, HTTPStatus.OK


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, HTTPStatus.OK
