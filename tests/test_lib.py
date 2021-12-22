from tests import BaseTest
from Api.libs import env
from unittest.mock import patch, call
from os import environ


class LibEnvTest(BaseTest):
    def test_env(self) -> None:
        key = "NOT EXISTING KEY"
        with self.assertRaises(
            SystemExit,
        ):
            with patch("builtins.print") as mocked_print:
                env.get_env_path(key)
                assert mocked_print.mock_calls == [call(f"Missing {key} env!")]

    def test_env_not_in_dot(self) -> None:
        key = "NEWKEY"
        value = "test"
        environ[key] = value
        res = env.get_env_path(key)
        assert res == value


# class LibMailTest(BaseTest):
#     def test_error_send_invalid_mail(self) -> None:
#         with self.assertRaises(
#             UserInvalidEmail,
#         ):
#             mail.Mail.send_email(
#                 ["opendrive.noreply@g@m@a@i@l.com"], "test", "test", "<div>test</div>"
#             )
