from http import HTTPStatus

from Api.models.user import UserModel
from Api.schemas.user import UserSchema

from tests import BaseTest


class JwtTest(BaseTest):
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

    def test_error_access_token_banned(self) -> None:
        response = self.client.post(
            "/api/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": "guest",
                "password": "1234",
            },
        )

        access_token = response.json["access_token"]

        response = self.client.post(
            "/api/logout",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )

        response = self.client.get(
            "/api/user",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "Token has been revoked"
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
