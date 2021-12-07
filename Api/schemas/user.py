from Api.ma import ma
from Api.models.user import UserModel
from marshmallow import Schema, fields, pre_dump
from marshmallow_sqlalchemy.schema import auto_field


class TokenReturnSchema(Schema):
    access_token = fields.String(required=True, description="The jwt access token")
    refresh_token = fields.String(required=False, description="The jwt refresh token")
    expires = fields.Integer(required=False, description="The jwt expiration time")


class UserLoginPostRequestSchema(ma.SQLAlchemySchema):
    # api_type = fields.String(required=True, description="API type of awesome API")
    # Il required sta in sqlachymy, se è nullable li è required qui
    class Meta:
        model = UserModel

    username = auto_field()
    password = auto_field()


class UserPostRequestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel
        # Solo per caricamento, non in get
        load_only = ("password",)

    name = auto_field()
    username = auto_field()
    surname = auto_field()
    password = auto_field()
    email = auto_field()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        load_only = ("password",)
        dump_only = (
            "id",
            "confirmation",
        )
        partial = ("role_id",)

    role_id = auto_field()
