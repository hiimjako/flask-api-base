from marshmallow_sqlalchemy.schema import auto_field
from Api.models.user import UserModel
from Api.ma import ma
from marshmallow import pre_dump, Schema, fields


class TokenReturnSchema(Schema):
    access_token = fields.String(required=True, description="The jwt access token")
    refresh_token = fields.String(required=False, description="The jwt refresh token")


class UserLoginPostRequestSchema(ma.SQLAlchemyAutoSchema):
    # api_type = fields.String(required=True, description="API type of awesome API")
    # Il required sta in sqlachymy, se è nullable li è required qui
    class Meta:
        model = UserModel
        fields = (
            "username",
            "password",
        )


class UserPostRequestSchema(ma.SQLAlchemyAutoSchema):
    # api_type = fields.String(required=True, description="API type of awesome API")
    # Il required sta in sqlachymy, se è nullable li è required qui
    class Meta:
        model = UserModel
        # Solo per caricamento, non in get
        load_only = ("password",)
        # Solo in get non in post
        dump_only = (
            "id",
            "confirmation",
        )


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

    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
