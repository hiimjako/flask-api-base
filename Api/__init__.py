import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, jsonify
from flask_apispec.extension import FlaskApiSpec
from flask_mail import Mail
from flask_restful import Api
from marshmallow import ValidationError

import Api.errors as APIException
from Api.config import config as Config
from Api.db import db, migrate, redis_client
from Api.errors.app import InvalidConfigurationName
from Api.jwt import jwt
from Api.resources.confirmation import Confirmation
from Api.resources.user import (
    SelfUser,
    TokenRefresh,
    User,
    UserLogin,
    UserLogout,
    UserRegister,
    UserRestoreCredentials,
)
from http import HTTPStatus

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()


def create_app(config: str = "development", verbose: bool = True) -> "Flask":
    """Creates the main flask app"""
    config_name = config
    if not isinstance(config, str):
        config_name = os.environ.get("FLASK_ENV") or "development"
    if config_name not in Config:
        raise InvalidConfigurationName(config_name)
    if verbose:
        Config[config_name].verbose()

    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(Config[config_name]())
    app.config.update(
        {
            "APISPEC_SPEC": APISpec(
                title="Awesome Project",
                version="v1",
                plugins=[MarshmallowPlugin()],
                openapi_version="2.0.0",
            ),
            "APISPEC_SWAGGER_URL": "/swagger/",  # URI to access API Doc JSON
            "APISPEC_SWAGGER_UI_URL": "/swagger-ui/",  # URI to access UI of API Doc
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_ERROR_MESSAGE_KEY": "message",
            # "PROPAGATE_EXCEPTIONS": True
        }
    )

    api = Api(app, "/api", errors=APIException.errors)
    db.init_app(app)
    redis_client.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    docs = FlaskApiSpec(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), HTTPStatus.BAD_REQUEST

    @app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
    def handle_unprocessable_entity(err):
        exc = getattr(err, "exc")
        if exc:
            messages = exc.messages
            if "json" in messages:
                messages = messages["json"]
        else:
            messages = ["Invalid request"]
        return jsonify({"status": "error", "result": messages}), HTTPStatus.BAD_REQUEST

    # @app.after_request
    # def refresh_expiring_jwts(response):
    #     """auto refresh token"""
    #     try:
    #         exp_timestamp = get_jwt_manager()["exp"]
    #         now = datetime.now(datetime.timezone.utc)
    #         target_timestamp = datetime.timestamp(now + datetime.timedelta(minutes=30))
    #         if target_timestamp > exp_timestamp:
    #             access_token = create_access_token(
    #                 identity=get_jwt_identity(), fresh=False
    #             )
    #             set_access_cookies(response, access_token)
    #         return response
    #     except (RuntimeError, KeyError):
    #         # Case where there is not a valid JWT. Just return the original respone
    #         return response
    #     except Exception:
    #         return response

    api.add_resource(UserRegister, "/register")
    api.add_resource(SelfUser, "/user")
    api.add_resource(UserRestoreCredentials, "/user/credential")
    api.add_resource(User, "/user/<int:user_id>")
    api.add_resource(TokenRefresh, "/token/refresh")
    api.add_resource(UserLogin, "/login")
    api.add_resource(UserLogout, "/logout")
    api.add_resource(Confirmation, "/user_confirm/<string:confirmation_token>")

    docs.register(User)
    docs.register(SelfUser)
    docs.register(UserRegister)
    docs.register(UserRestoreCredentials)
    docs.register(Confirmation)

    return app
