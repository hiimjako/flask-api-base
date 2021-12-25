from http import HTTPStatus
from Api.libs.strings import gettext

from Api.models.permission import DEFAULT_ROLE, Permission
from Api.models.user import UserModel
from Api.schemas.user import UserSchema

from tests import BaseTest

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)


class UserModelTest(BaseTest):
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
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest2",
            "password": "1234",
            "email": "opendrive.noreply2@gmail.com",
            "role_id": 2,
            "confirmed": True,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_repr(self) -> None:
        ret = UserModel.find_by_username("guest")
        assert ret.__repr__() == "<User ('guest', 'opendrive.noreply@gmail.com')>"

    def test_find_by_username(self) -> None:
        ret = UserModel.find_by_username("guest")
        assert ret.id == 1
        assert ret.name == "Guest"
        assert ret.surname == "test"
        assert ret.username == "guest"
        assert ret.email == "opendrive.noreply@gmail.com"
        assert ret.role_id == 1
        assert ret.confirmed == True

    def test_can(self) -> None:
        user = UserModel.find_by_username("guest")
        ret = user.can(Permission.ADMINISTER)
        assert ret == True
        ret = user.can(Permission.STUDENT)
        assert ret == True
        ret = user.can(Permission.TEACHER)
        assert ret == True

        user = UserModel.find_by_username("guest2")
        ret = user.can(Permission.ADMINISTER)
        assert ret == False
        ret = user.can(Permission.STUDENT)
        assert ret == False
        ret = user.can(Permission.TEACHER)
        assert ret == True

    def test_password(self) -> None:
        pasw = "supersecurepass"
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": pasw,
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
            "confirmed": True,
        }
        user: UserModel = UserSchema().load(user_json)
        user.hash_password()
        assert user.password != pasw
        ret = user.verify_password(pasw)
        assert ret == True
        ret = user.verify_password("wrongpsw")
        assert ret == False

    def test_create_confirmation_token_error(self) -> None:
        user = UserModel.find_by_username("guest")
        with self.assertRaises(
            Exception,
        ):
            user_by_token = user.generate_confirmation_token("ciao")

    def test_confirmation_token(self) -> None:
        user = UserModel.find_by_username("guest")
        token = user.generate_confirmation_token()
        user_by_token = UserModel.user_by_token(token)
        assert user.id == user_by_token.id

    def test_confirmation_token_expired(self) -> None:
        user = UserModel.find_by_username("guest")
        token = user.generate_confirmation_token(expiration=0.01)
        with self.assertRaises(
            Exception,
        ):
            user_by_token = UserModel.user_by_token(token)

    def test_confirmation_invalid_token(self) -> None:
        with self.assertRaises(
            Exception,
        ):
            user_by_token = UserModel.user_by_token("invalid")

    def test_save_to_db(self) -> None:
        user = UserModel.find_by_username("guest")
        user.name = "new name"
        user.save_to_db()
        ret = UserModel.find_by_username("guest")
        assert ret.name == "new name"

    def test_delete(self) -> None:
        ret = UserModel.find_by_username("guest")
        ret.delete_from_db()
        ret = UserModel.find_by_username("guest")
        assert ret is None


class LoginTest(BaseTest):
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
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()
        user_json = {
            "name": "Not confirmed",
            "surname": "user",
            "username": "not_confirmed_user",
            "password": "1234",
            "email": "opendrive.noreply2@gmail.com",
            "role_id": 1,
            "confirmed": False,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_login(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )

        # Then
        assert "access_token" in response.json
        assert "expires" in response.json
        assert "refresh_token" in response.json
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_invalid_credentials(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "wrong password",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "User credentials invalid."
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

    def test_not_confirmed(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "not_confirmed_user",
                "password": "1234",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "User not yet confirmed."
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)


class LogoutTest(BaseTest):
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
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_logout(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )

        response = self.client.post(
            "/api/logout",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {response.json['access_token']}",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == gettext("user_logged_out").format(1)

        self.assertEqual(HTTPStatus.OK, response.status_code)


class RefreshTokenTest(BaseTest):
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
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successfull_refresh(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )
        response = self.client.post(
            "/api/token/refresh",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {response.json['refresh_token']}",
            },
        )

        assert "access_token" in response.json
        assert "expires" in response.json
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_unsuccessfull_refresh(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )

        response = self.client.post(
            "/api/token/refresh",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {response.json['refresh_token'][:-7]}invalid",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "Signature verification failed"

        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)


class UserRegisterTest(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

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
        userSchema: UserModel = UserSchema().dump(user)

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

    def test_unique_email(self) -> None:
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

    def test_unique_username(self) -> None:
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


class UserCredentialsTest(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "old1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
            "confirmed": True,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

        self.user_token = {
            "access_token": create_access_token(user.id, fresh=True),
            "refresh_token": create_refresh_token(user.id),
        }

    def test_update_password(self) -> None:
        response = self.client.put(
            "/api/user/credential",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.user_token['access_token']}",
            },
            json={"old_password": "old1234", "new_password": "test1234"},
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)

        user = UserModel.find_by_username("guest")
        res = user.verify_password("test1234")
        assert res == True

    def test_update_password_fresh_token_needed(self) -> None:
        user = UserModel.find_by_username("guest")
        response = self.client.put(
            "/api/user/credential",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {create_access_token(user.id, fresh=False)}",
            },
            json={"old_password": "old1234", "new_password": "test1234"},
        )

        assert "message" in response.json
        assert response.json["message"] == "Fresh token required"
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

    def test_update_password_invalid_user(self) -> None:
        response = self.client.put(
            "/api/user/credential",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {create_access_token(20, fresh=True)}",
            },
            json={"old_password": "old1234", "new_password": "test1234"},
        )

        assert "message" in response.json
        assert response.json["message"] == "User not found."
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)


class SelfUserTest(BaseTest):
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
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_get_user_info(self) -> None:
        response = self.client.get(
            "/api/user",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {create_access_token(1, fresh=True)}",
            },
        )

        userSchema: UserModel = UserSchema().dump(response.json)

        self.assertEqual(
            userSchema,
            {
                "avatar": None,
                "name": "Guest",
                "username": "guest",
                "confirmed": True,
                "role_id": 1,
                "id": 1,
                "surname": "test",
                "email": "opendrive.noreply@gmail.com",
            },
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_error_no_user_found(self) -> None:
        response = self.client.get(
            "/api/user",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {create_access_token(9999, fresh=True)}",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "User not found."
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_successful_update_user_info(self) -> None:
        new_user_info = {
            "avatar": "img.png",
            "name": "new name",
            "role_id": 2,
            "surname": "new surname",
            "email": "opendrive.noreply2@gmail.com",
        }

        response = self.client.put(
            "/api/user",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {create_access_token(1, fresh=True)}",
            },
            json=new_user_info,
        )

        userSchema: UserModel = UserSchema().dump(response.json)

        self.assertEqual(
            userSchema,
            {
                "avatar": "img.png",
                "name": "new name",
                "username": "guest",
                "confirmed": True,
                "role_id": 2,
                "id": 1,
                "surname": "new surname",
                "email": "opendrive.noreply2@gmail.com",
            },
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
