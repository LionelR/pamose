"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = 'PAMOSE_SECRET_KEY'  # TODO: Change me (in install process?)
    TOKEN_EXPIRATION_TIME = 3600
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    # DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
    LOG_DIR = '/tmp'
    LOG_LEVEL = 'WARNING'
    LOG_FORMAT = '<%(asctime)s> <%(levelname)s> %(message)s'


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
