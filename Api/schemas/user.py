from Api.ma import ma
from Api.models.user import UserModel
from marshmallow import Schema, fields
from marshmallow_sqlalchemy.schema import auto_field


class TokenReturnSchema(Schema):
    access_token = fields.String(required=True, description="The jwt access token")
    refresh_token = fields.String(required=False, description="The jwt refresh token")
    expires = fields.Integer(required=False, description="The jwt expiration time")


class UserUpdatePutCredentials(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    old_password = fields.String(required=True, description="The old password")
    new_password = auto_field("password", attribute="new_password")


class UserUpdatePostCredentials(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    username = auto_field()
    email = auto_field()


class UserCredentialsPostExternal(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    password = auto_field("password")


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
        load_only = (
            "password",
            "confirmation",
        )
        dump_only = ()
        partial = ("role_id",)

    role_id = auto_field()


class UserPutRequestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    name = auto_field(required=False)
    username = auto_field(required=False)
    surname = auto_field(required=False)
    email = auto_field(required=False)
    avatar = auto_field(required=False)
    role_id = auto_field(required=False)
