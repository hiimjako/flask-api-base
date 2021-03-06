import traceback
from http import HTTPStatus

import Api.errors.user as UserException
from Api.decorators import admin_required, doc_with_jwt
from Api.jwt import (
    create_refresh_token_and_store,
    delete_token_into_redis,
    get_current_user_wrapper,
    get_expire_time_by_type,
    save_token_into_redis,
)
from Api.libs.strings import gettext
from Api.models.user import UserModel
from Api.schemas.common import GenericReturnSchema
from Api.schemas.user import (
    TokenReturnSchema,
    UserCredentialsPostExternal,
    UserLoginPostRequestSchema,
    UserPostRequestSchema,
    UserPutRequestSchema,
    UserSchema,
    UserUpdatePostCredentials,
    UserUpdatePutCredentials,
)
from flask import after_this_request, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    get_jti,
)
from flask_jwt_extended.utils import set_refresh_cookies, unset_jwt_cookies
from flask_restful import Resource


class UserRegister(MethodResource, Resource):
    @doc(description="Insert user.", tags=["User"])
    @use_kwargs(UserPostRequestSchema, location=("json"))
    # parso solo quello che voglio, le cose in più rimosse
    @marshal_with(GenericReturnSchema)
    def post(self, **kwargs):
        # user_json = request.get_json()
        user_json = kwargs
        user = UserSchema().load(user_json, partial=("role_id",))

        if UserModel.find_by_username(user.username):
            raise UserException.UsernameAlreadyExists

        if UserModel.find_by_email(user.email):
            raise UserException.UserEmailAlreadyExists

        try:
            # FIXME: set default
            user.save_user_and_update_password()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, HTTPStatus.CREATED
        except UserException.UserInvalidEmail:
            user.delete_from_db()  # rollback
            raise
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback
            raise UserException.UserCreate


class User(MethodResource, Resource):
    @doc(description="Get user information.", tags=["User"])
    @marshal_with(UserSchema())
    @jwt_required()
    @admin_required
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
    @admin_required
    def delete(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            raise UserException.UserNotFound

        user.delete_from_db()
        return {"message": gettext("user_deleted")}, HTTPStatus.OK


class SelfUser(MethodResource, Resource):
    @doc_with_jwt(description="Get logged user information.", tags=["User"])
    @marshal_with(UserSchema())
    @jwt_required()
    def get(self):
        user = get_current_user_wrapper()
        # if not user: # not needed
        #     raise UserException.UserNotFound

        return user, HTTPStatus.OK

    @doc_with_jwt(description="Update logged user information.", tags=["User"])
    @use_kwargs(UserPutRequestSchema, location=("json"))
    @marshal_with(UserSchema())
    @jwt_required()
    def put(self, **kwargs):
        user = get_current_user_wrapper()
        # if not user: # not needed
        #     raise UserException.UserNotFound

        user_json = kwargs

        for k, v in user_json.items():
            try:
                if hasattr(user, k):
                    user.__setattr__(k, v)
            except:  # pragma: no cover
                pass

        user.save_to_db()

        return user, HTTPStatus.OK


class UserLogin(MethodResource, Resource):
    @doc(description="Login user with credentials.", tags=["User"])
    @use_kwargs(UserLoginPostRequestSchema, location=("json"))
    @marshal_with(TokenReturnSchema)
    def post(self, **kwargs):
        # user_json = request.get_json()
        user_json = kwargs
        user_data = UserLoginPostRequestSchema().load(user_json)

        user = UserModel.find_by_username(user_data["username"])

        if user and user.verify_password(user_data["password"]):
            if user.confirmed:
                access_token = create_access_token(user.id, fresh=True)
                refresh_token = create_refresh_token_and_store(user.id)

                @after_this_request
                def set_cookie_value(response):
                    set_refresh_cookies(response, refresh_token)
                    return response

                return (
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires": get_expire_time_by_type("access").seconds,
                    },
                    HTTPStatus.OK,
                )
            raise UserException.UserNotConfirmed
        raise UserException.UserInvalidCredentials


class UserCredentials(MethodResource, Resource):
    @doc(
        description="Restore user credentials sending email to generate a new one.",
        tags=["User"],
    )
    @use_kwargs(UserUpdatePostCredentials, location=("json"))
    @marshal_with(TokenReturnSchema)
    def post(self, **kwargs):
        # TODO: send email and new password
        # user_json = request.get_json()
        user_json = kwargs
        user = UserModel.find_by_username(user_json["username"])

        if user is None:
            raise UserException.UserNotFound

        if user.email != user_json["email"]:
            raise UserException.UserInvalidEmail

        if not user.confirmed:
            raise UserException.UserNotConfirmed

        user.send_reset_password_email()

        return (
            {
                "message": gettext("user_reset_password_email").format(user.id),
            },
            HTTPStatus.OK,
        )

    @doc_with_jwt(description="Update user credentials.", tags=["User"])
    @use_kwargs(UserUpdatePutCredentials, location=("json"))
    @marshal_with(TokenReturnSchema)
    @jwt_required(fresh=True)
    def put(self, **kwargs):
        user = get_current_user_wrapper()
        # if not user: # not needed
        #     raise UserException.UserNotFound

        user_json = kwargs

        if user and user.verify_password(user_json["old_password"]):
            if user.confirmed:
                user.password = user_json["new_password"]
                user.save_user_and_update_password()
                access_token = create_access_token(user.id, fresh=True)
                refresh_token = create_refresh_token_and_store(user.id)

                @after_this_request
                def set_cookie_value(response):
                    set_refresh_cookies(response, refresh_token)
                    return response

                return (
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires": get_expire_time_by_type("access").seconds,
                    },
                    HTTPStatus.OK,
                )
            raise UserException.UserNotConfirmed
        raise UserException.UserInvalidCredentials


class UserCredentialsExternal(MethodResource, Resource):
    @doc(
        description="Restore user credentials sending email to generate a new one.",
        params={
            "reset_token": {
                "description": "The ID of the confirmation",
                "example": "cdb93c441cee49ada0527862b7f73350",
            },
        },
        tags=["User"],
    )
    @use_kwargs(UserCredentialsPostExternal, location=("json"))
    @marshal_with(GenericReturnSchema)
    def post(self, reset_token: str, **kwargs):

        user = UserModel.user_by_token(reset_token)
        if not user:
            raise UserException.UserNotFound

        user_json = kwargs
        user.password = user_json["password"]
        user.save_user_and_update_password()

        return {"message": gettext("user_reset_password_successful")}, HTTPStatus.OK


class UserLogout(MethodResource, Resource):
    @doc_with_jwt(description="Logut user.", tags=["User"])
    @marshal_with(GenericReturnSchema)
    @jwt_required()
    def post(self):
        # https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        jwt_type = get_jwt()["type"]
        user_id = get_jwt_identity()

        save_token_into_redis(jwt_type, jti, user_id)

        try:
            refresh_token = request.cookies["refresh_token_cookie"]
            delete_token_into_redis("refresh", get_jti(refresh_token), user_id)
        except:  # pragma: no cover
            print(f"[WARNING] On logout no refresh_token given, user: {user_id}")

        @after_this_request
        def unset_cookie_value(response):
            unset_jwt_cookies(response)
            return response

        return {"message": gettext("user_logged_out").format(user_id)}, HTTPStatus.OK


class TokenRefresh(MethodResource, Resource):
    @marshal_with(TokenReturnSchema)
    @jwt_required(refresh=True)
    def post(self):
        """If @jwt_required(refresh=True) i get in get_jwt() the refresh token"""
        user_id = get_jwt_identity()
        new_token = create_access_token(identity=user_id, fresh=False)
        return {
            "access_token": new_token,
            "expires": get_expire_time_by_type("access").seconds,
        }, HTTPStatus.OK
