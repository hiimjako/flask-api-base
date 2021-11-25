from flask_jwt_extended import JWTManager

from Api.blocklist import BLOCKLIST
from Api.models.user import UserModel
import Api.errors.user as UserException

jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.user_identity_loader
def _user_identity_lookup(user_id: int):
    return user_id


@jwt.user_lookup_loader
def _user_lookup_callback(_jwt_header, jwt_data) -> "UserModel":
    identity = jwt_data["sub"]
    user = UserModel.find_by_id(identity)
    if not user:
        raise UserException.UserNotFound
    return user
