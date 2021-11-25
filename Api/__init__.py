import os

from flask import Flask, jsonify
from flask_mail import Mail
from flask_restful import Api
from marshmallow import ValidationError

from Api.jwt import jwt
from Api.config import config as Config
from Api.db import db, migrate
from Api.errors.app import InvalidConfigurationName
from Api.ma import ma
from Api.resources.confirmation import Confirmation, ConfirmationByUser
from Api.resources.user import TokenRefresh, User, UserLogin, UserLogout, UserRegister
import Api.errors as APIException
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()


def create_app(config: str) -> "Flask":
    """Creates the main flask app"""
    config_name = config
    if not isinstance(config, str):
        config_name = os.environ.get("FLASK_ENV") or "development"
    if config_name not in Config:
        raise InvalidConfigurationName(config_name)

    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(Config[config_name])
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
            "JWT_TOKEN_LOCATION": ["headers"]
            # "PROPAGATE_EXCEPTIONS": True
        }
    )

    Config[config_name].init_app(app)

    api = Api(app, errors=APIException.errors)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    docs = FlaskApiSpec(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    api.add_resource(UserRegister, "/register")
    api.add_resource(User, "/user/<int:user_id>")
    api.add_resource(UserLogin, "/login")
    api.add_resource(TokenRefresh, "/refresh")
    api.add_resource(UserLogout, "/logout")
    api.add_resource(Confirmation, "/user_confirm/<string:confirmation_id>")
    api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")

    docs.register(User)
    docs.register(UserRegister)
    docs.register(UserLogout)
    docs.register(UserLogin)
    docs.register(Confirmation)
    docs.register(ConfirmationByUser)

    return app
