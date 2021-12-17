from http import HTTPStatus
from Api.models.permission import DEFAULT_ROLE

from Api.models.user import UserModel
from Api.schemas.user import UserSchema

from tests import BaseTest


class SignupTest(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
            "confirmed": True,
        }
        user = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_signup(self) -> None:
        response = self.client.post(
            "/api/token/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )

        # Then
        assert "access_token" in response.json
        assert "refresh_token" in response.json
        self.assertEqual(HTTPStatus.OK, response.status_code)


class UserRegister(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
        }
        user = UserSchema().load(user_json)
        user.save_to_db()

    def test_successful_register(self) -> None:
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest2",
            "password": "1234",
            "email": "opendrive2.noreply@gmail.com",
        }

        response = self.client.post(
            "/api/register",
            headers={"Content-Type": "application/json"},
            json=user_json,
        )

        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        user = UserModel.find_by_id(2)
        userSchema = UserSchema().dump(user)

        self.assertEqual(
            userSchema,
            {
                "id": 2,
                "name": "Guest",
                "surname": "test",
                "email": "opendrive2.noreply@gmail.com",
                "username": "guest2",
                "avatar": None,
                "role_id": DEFAULT_ROLE,
                "confirmed": False,
            },
        )

    def test_wrong_email(self) -> None:
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest2",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
        }

        response = self.client.post(
            "/api/register",
            headers={"Content-Type": "application/json"},
            json=user_json,
        )

        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)

    def test_wrong_username(self) -> None:
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive2.noreply@gmail.com",
        }

        response = self.client.post(
            "/api/register",
            headers={"Content-Type": "application/json"},
            json=user_json,
        )

        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)
