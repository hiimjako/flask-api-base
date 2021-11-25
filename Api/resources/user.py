import traceback
from http import HTTPStatus

import Api.errors.user as UserException
from Api.blocklist import BLOCKLIST
from Api.decorators import doc_with_jwt
from Api.libs.strings import gettext
from Api.models.confirmation import ConfirmationModel
from Api.models.user import UserModel
from Api.schemas.common import GenericReturnSchema
from Api.schemas.user import (
    TokenReturnSchema,
    UserLoginPostRequestSchema,
    UserPostRequestSchema,
    UserSchema,
)
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource

user_schema = UserSchema()


class UserRegister(MethodResource, Resource):
    @doc(description="Insert user.", tags=["User"])
    @use_kwargs(UserPostRequestSchema, location=("json"))
    # parso solo quello che voglio, le cose in più rimosse
    @marshal_with(GenericReturnSchema)
    def post(self, **kwargs):
        # user_json = request.get_json()
        user_json = kwargs
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            raise UserException.UsernameAlreadyExistsError

        if UserModel.find_by_email(user.email):
            raise UserException.UserEmailAlreadyExistsError

        try:
            user.hash_password()
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, HTTPStatus.CREATED
        except UserException.UserInvalidEmail:
            user.delete_from_db()  # rollback
            raise UserException.UserInvalidEmail
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback
            raise UserException.UserCreateError


class User(MethodResource, Resource):
    # TODO: TO REMOVE
    @doc(description="Get user information.", tags=["User"])
    @marshal_with(user_schema)
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        return user, HTTPStatus.OK

    @doc_with_jwt(
        description="Delete a user. (only for admin)",
        params={"Authorization": {"description": "ciao"}},
        tags=["User"],
    )
    @jwt_required()
    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        user.delete_from_db()
        return {"message": gettext("user_deleted")}, HTTPStatus.OK


class UserLogin(MethodResource, Resource):
    @doc(description="Login user with credentials.", tags=["User"])
    @use_kwargs(UserLoginPostRequestSchema, location=("json"))
    @marshal_with(TokenReturnSchema)
    def post(self, **kwargs):
        # user_json = request.get_json()
        user_json = kwargs
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        if user and user.verify_password(user_data.password):
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


class UserLogout(MethodResource, Resource):
    @doc_with_jwt(description="Logut user.", tags=["User"])
    @marshal_with(GenericReturnSchema)
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLOCKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, HTTPStatus.OK


class TokenRefresh(MethodResource, Resource):
    @marshal_with(TokenReturnSchema)
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, HTTPStatus.OK
