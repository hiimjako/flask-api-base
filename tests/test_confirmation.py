from http import HTTPStatus


from Api.models.user import UserModel
from Api.schemas.user import UserSchema

from tests import BaseTest


class ConfirmationTest(BaseTest):
    def populate_db(self):
        user_json = {
            "name": "Guest",
            "surname": "test",
            "username": "guest",
            "password": "1234",
            "email": "opendrive.noreply@gmail.com",
            "role_id": 1,
            "confirmed": False,
        }
        user: UserModel = UserSchema().load(user_json)
        user.save_user_and_update_password()

    def test_successful_confirmation(self) -> None:
        user = UserModel.find_by_username("guest")
        token = user.generate_external_token().decode("utf-8")
        response = self.client.get(
            f"/api/user_confirm/{token}",
            headers={
                "Content-Type": "application/json",
            },
        )

        assert response.json == None
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_error_no_user_found(self) -> None:
        user = UserModel.find_by_username("guest")
        token = user.generate_external_token().decode("utf-8")
        user.delete_from_db()
        response = self.client.get(
            f"/api/user_confirm/{token}",
            headers={
                "Content-Type": "application/json",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "User not found."
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_error_user_already_confirmed(self) -> None:
        user = UserModel.find_by_username("guest")
        token = user.generate_external_token().decode("utf-8")
        user.confirmed = True
        user.save_to_db()
        response = self.client.get(
            f"/api/user_confirm/{token}",
            headers={
                "Content-Type": "application/json",
            },
        )

        assert "message" in response.json
        assert response.json["message"] == "The user has been already confirmed."
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
