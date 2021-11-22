import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from marshmallow import ValidationError

from Api.config import config as Config
from Api.blocklist import BLOCKLIST
from Api.db import db, migrate
from Api.ma import ma
from Api.resources.user import (TokenRefresh, User, UserLogin, UserLogout,
                            UserRegister)

basedir = os.path.abspath(os.path.dirname(__file__))

def create_app(config: str) -> "Flask":
    """Creates the main flask app"""
    config_name = config
    if not isinstance(config, str):
        config_name = os.environ.get("FLASK_ENV") or "development" 
    
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(Config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    Config[config_name].init_app(app)

    api = Api(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    # This method will check if a token is blocklisted, and will be called automatically when blocklist is enabled
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST


    api.add_resource(UserRegister, "/register")
    api.add_resource(User, "/user/<int:user_id>")
    api.add_resource(UserLogin, "/login")
    api.add_resource(TokenRefresh, "/refresh")
    api.add_resource(UserLogout, "/logout")

    return app

