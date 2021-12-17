from datetime import timedelta
from flask import current_app
from flask_jwt_extended import JWTManager
from flask_jwt_extended.utils import get_current_user

import Api.errors.user as UserException
from Api import redis_client
from Api.models.user import UserModel

jwt = JWTManager()

JWT_PREFIX_ACCESS_TOKEN_REDIS = "access"
JWT_PREFIX_REFRESH_TOKEN_REDIS = "refresh"


def get_expire_time_by_type(jwt_type: str) -> timedelta:
    if jwt_type == "access":
        return current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    if jwt_type == "refresh":
        return current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]


def get_redis_prefix_by_type(jwt_type: str) -> str:
    if jwt_type == "access":
        return JWT_PREFIX_ACCESS_TOKEN_REDIS
    if jwt_type == "refresh":
        return JWT_PREFIX_REFRESH_TOKEN_REDIS


# https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload) -> bool:
    jti = jwt_payload["jti"]
    jwt_type = jwt_payload["type"]
    prefix = get_redis_prefix_by_type(jwt_type)

    token_in_redis = redis_client.get(f"{prefix}:{jti}")
    return token_in_redis is not None


@jwt.user_identity_loader
def _user_identity_lookup(user_id: int) -> int:
    return user_id


@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data) -> "UserModel":
    identity = jwt_data["sub"]
    user = UserModel.find_by_id(identity)
    if not user:
        raise UserException.UserNotFound
    return user


def get_current_user_wrapper() -> "UserModel":
    return get_current_user()
