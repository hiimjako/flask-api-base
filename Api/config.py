from datetime import timedelta
from os import path

from Api.libs.env import get_env_path

basedir = path.abspath(path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_SESSION_COOKIE = False
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    # se true si eliminano dopo la chiusura del browser

    UPLOAD_PATH = path.join(basedir, "upload")

    ENCRTYPTION_KEY = get_env_path("ENCRTYPTION_KEY")
    JWT_SECRET_KEY = ENCRTYPTION_KEY

    POSTGRES_USER = get_env_path("POSTGRES_USER")
    POSTGRES_PASSWORD = get_env_path("POSTGRES_PASSWORD")
    POSTGRES_URL = get_env_path("POSTGRES_URL") or "127.0.0.1"
    POSTGRES_PORT = get_env_path("POSTGRES_PORT") or 5432
    POSTGRES_DB = get_env_path("POSTGRES_DB")

    REDIS_HOST = get_env_path("REDIS_HOST") or "127.0.0.1"
    REDIS_PORT = get_env_path("REDIS_PORT") or 6379
    REDIS_PASSWORD = get_env_path("REDIS_PASSWORD")
    REDIS_DB = get_env_path("REDIS_DB") or 0

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
    def verbose(app):
        pass

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_URL}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self):
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class ProductionConfig(Config):
    FLASK_ENV = "production"

    @classmethod
    def verbose(cls):
        print("PRODUCTION")


class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    JWT_COOKIE_SECURE = False
    # Only to debug purpose
    SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"

    @classmethod
    def verbose(cls):
        print("THIS APP IS IN DEBUG MODE")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    REDIS_HOST = "127.0.0.1"
    REDIS_DB = 10

    @classmethod
    def verbose(cls):
        print("THIS APP IS IN TEST MODE.")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestingConfig,
}
