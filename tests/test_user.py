from Api.schemas.user import UserSchema
from tests import BaseTest


class SignupTest(BaseTest):
    # def populate_db(self):
    #     user_json = {
    #         "username": "guest",
    #         "password": "1234",
    #         "email": "moretti919@gmail.com"
    #     }
    #     user = UserSchema().load(user_json)
    #     user.save_to_db()

    def test_successful_signup(self):
        response = self.client.get(
            "/user/1", headers={"Content-Type": "application/json"}
        )

        # Then
        self.assertEqual(
            response.json,
            {"id": 1, "email": "moretti919@gmail.com", "username": "guest"},
        )
        self.assertEqual(200, response.status_code)
