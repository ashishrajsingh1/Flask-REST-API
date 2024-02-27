import os
from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


class Config:
    API_TITLE = config.get('Flask', 'API_TITLE', fallback="Stores REST API")
    API_VERSION = config.get('Flask', 'API_VERSION', fallback="v1")
    OPENAPI_VERSION = config.get('Flask', 'OPENAPI_VERSION', fallback="3.0.3")
    OPENAPI_URL_PREFIX = config.get('Flask', 'OPENAPI_URL_PREFIX', fallback="/")
    OPENAPI_SWAGGER_UI_PATH = config.get('Flask', 'OPENAPI_SWAGGER_UI_PATH', fallback="/swagger-ui")
    OPENAPI_SWAGGER_UI_URL = config.get('Flask', 'OPENAPI_SWAGGER_UI_URL',
                                        fallback="https://cdn.jsdelivr.net/npm/swagger-ui-dist/")
    SQLALCHEMY_TRACK_MODIFICATIONS = config.getboolean('Flask', 'SQLALCHEMY_TRACK_MODIFICATIONS', fallback=False)
    PROPAGATE_EXCEPTIONS = config.getboolean('Flask', 'PROPAGATE_EXCEPTIONS', fallback=True)
    JWT_SECRET_KEY = config.get('Flask', 'JWT_SECRET_KEY', fallback="jose")
    SECRET_KEY = config.get('Flask', 'SECRET_KEY', fallback="1234")
    SQLALCHEMY_DATABASE_URI = config.get('Flask', 'SQLALCHEMY_DATABASE_URI', fallback="sqlite:///data.db")
