from Api import create_app
from Api.errors.app import InvalidConfigurationName
from tests import BaseTest
from unittest.mock import patch, call


class ConfigTest(BaseTest):
    def test_error_wrong_configname(self) -> None:
        not_valid_config = "Not a valid config"
        with self.assertRaises(
            InvalidConfigurationName,
            msg=f"configuration name '{not_valid_config}' is not in (development, production, test)",
        ):
            create_app(not_valid_config)

    def test_default_config(self) -> None:
        with patch("builtins.print") as mocked_print:
            app = create_app(None, True)
            assert mocked_print.mock_calls == [call("THIS APP IS IN DEVELOPMENT MODE")]

    def test_verbose(self) -> None:
        with patch("builtins.print") as mocked_print:
            app = create_app("development", True)
            assert mocked_print.mock_calls == [call("THIS APP IS IN DEVELOPMENT MODE")]
        with patch("builtins.print") as mocked_print:
            app = create_app("production", True)
            assert mocked_print.mock_calls == [call("PRODUCTION")]
        with patch("builtins.print") as mocked_print:
            app = create_app("test", True)
            assert mocked_print.mock_calls == [call("THIS APP IS IN TEST MODE")]
