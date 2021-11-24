from os import environ, path

from Api.libs.env import get_env_path

basedir = path.abspath(path.dirname(__file__))

# Try better handling
if path.exists(".env"):
    for line in open(".env"):
        var = line.strip().split("=")
        if len(var) == 2:
            environ[var[0]] = var[1].replace('"', "")


class Config:
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = False

    UPLOAD_PATH = path.join(basedir, "upload")

    ENCRTYPTION_KEY = get_env_path("ENCRTYPTION_KEY")

    POSTGRES_USER = get_env_path("POSTGRES_USER")
    POSTGRES_PASSWORD = get_env_path("POSTGRES_PASSWORD")
    POSTGRES_URL = get_env_path("POSTGRES_URL")
    POSTGRES_PORT = get_env_path("POSTGRES_PORT")
    POSTGRES_DB = get_env_path("POSTGRES_DB")

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = get_env_path("MAIL_USERNAME")
    MAIL_PASSWORD = get_env_path("MAIL_PASSWORD")

    SECRET_KEY = get_env_path("SECRET_KEY")
    ADMIN_EMAIL = get_env_path("ADMIN_EMAIL")
    ADMIN_PASSWORD = get_env_path("ADMIN_PASSWORD")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_app(app):
        pass

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_URL}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class ProductionConfig(Config):
    FLASK_ENV = "production"

    @classmethod
    def init_app(cls, app):
        print("PRODUCTION")


class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    FLASK_RUN_HOST = "127.0.0.1"
    POSTGRES_URL = "127.0.0.1"
    DEBUG = True
    # Only to debug purpose
    SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"

    @classmethod
    def init_app(cls, app):
        print(
            "THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION."
        )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    @classmethod
    def init_app(cls, app):
        print(
            "THIS APP IS IN TEST MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION."
        )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestingConfig,
}
