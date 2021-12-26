from datetime import timedelta
from flask import current_app
from flask_jwt_extended import JWTManager
from flask_jwt_extended.utils import create_refresh_token, get_current_user, get_jti

import Api.errors.user as UserException
from Api import redis_client
from Api.models.user import UserModel

jwt_manager = JWTManager()

JWT_PREFIX_ACCESS_TOKEN_REDIS = "access"
JWT_PREFIX_REFRESH_TOKEN_REDIS = "refresh"


def save_token_into_redis(jwt_type: str, jti: str, user_id: int) -> None:
    redis_client.set(
        f"{user_id}:{get_redis_prefix_by_type(jwt_type)}:{jti}",
        "",
        ex=get_expire_time_by_type(jwt_type),
    )


def delete_token_into_redis(jwt_type: str, jti: str, user_id: int) -> None:
    redis_client.delete(
        f"{user_id}:{get_redis_prefix_by_type(jwt_type)}:{jti}",
    )


def delete_all_refresh_token_by_user_id(id: int) -> None:
    # Disable all old refresh token that now are invalid
    for key in redis_client.scan_iter(f"{id}:{get_redis_prefix_by_type('refresh')}:*"):
        redis_client.delete(key)


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
@jwt_manager.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload) -> bool:
    jti = jwt_payload["jti"]
    jwt_type = jwt_payload["type"]
    identity = jwt_payload["sub"]
    prefix = get_redis_prefix_by_type(jwt_type)
    token_in_redis = redis_client.get(f"{identity}:{prefix}:{jti}")

    # True -> revoked
    # False -> valid
    if jwt_type == "access":
        return token_in_redis is not None

    if jwt_type == "refresh":
        return token_in_redis is None

    # Revoked as default (unreachable)
    return True  # pragma: no cover


@jwt_manager.user_identity_loader
def _user_identity_lookup(user_id: int) -> int:
    return user_id


@jwt_manager.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data) -> "UserModel":
    identity = jwt_data["sub"]
    user = UserModel.find_by_id(identity)
    if not user:
        raise UserException.UserNotFound
    return user


def get_current_user_wrapper() -> "UserModel":
    return get_current_user()


def create_refresh_token_and_store(
    identity, expires_delta=None, additional_claims=None, additional_headers=None
) -> str:
    refresh_token = create_refresh_token(
        identity, expires_delta, additional_claims, additional_headers
    )
    save_token_into_redis("refresh", get_jti(refresh_token), identity)
    return refresh_token
