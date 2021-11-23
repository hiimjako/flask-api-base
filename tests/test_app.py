from Api import create_app
from Api.errors.app import InvalidConfigurationName
from tests import BaseTest


class ConfigTest(BaseTest):
    def test_error_wrong_configname(self) -> None:
        not_valid_config = "Not a valid config"
        with self.assertRaises(
            InvalidConfigurationName,
            msg=f"configuration name '{not_valid_config}' is not in (development, production, test)",
        ):
            create_app(not_valid_config)
