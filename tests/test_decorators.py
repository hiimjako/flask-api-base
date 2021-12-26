from flask_jwt_extended.view_decorators import jwt_required

from Api.decorators import permission_required
from Api.errors.user import UserHasNoPermission
from Api.models.permission import Permission
from Api.models.user import UserModel
from Api.schemas.user import UserSchema
from flask_jwt_extended import create_access_token

from tests import BaseTest


class DecoratorsTest(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 2,
            "confirmed": True,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_permission_required(self) -> None:
        @jwt_required()
        @permission_required(Permission.TEACHER)
        def foo():
            return True

        with self.app.test_request_context(
            "url",
            headers={"Authorization": f"Bearer {create_access_token(1, fresh=True)}"},
        ):
            ret = foo()
            assert ret == True

    def test_error_wrong_permission(self) -> None:
        @jwt_required()
        @permission_required(Permission.ADMINISTER)
        def foo():
            return True

        with self.assertRaises(
            UserHasNoPermission,
        ):
            with self.app.test_request_context(
                "url",
                headers={
                    "Authorization": f"Bearer {create_access_token(1, fresh=True)}"
                },
            ):
                foo()
