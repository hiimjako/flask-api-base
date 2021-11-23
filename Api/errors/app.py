from Api.config import config as Config 

class InvalidConfigurationName(Exception):
    """Rise when invalid configuration name (for flask api) is given"""
    
    def __init__(self, name):
        self.name = name
        self.valid_config_names = ", ".join(list(Config.keys())) or "development, production, test"
        self.message = "configuration name '{}' is not in ({})"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message.format(self.name, self.valid_config_names)}'