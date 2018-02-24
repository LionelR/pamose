"""
The app module, containing the app factory function.
"""
import os
from flask import Flask

from .default_settings import Config
from .models import db
from .schemas import ma
from .ressources import api
from . import commands

from .loggers import register as register_loggers
from .errorhandlers import register as register_errorhandlers
from .shellcontexts import register as register_shellcontexts


def create_app(config=None):
    """
    The Flask Application creating function
    :type config: dict. An optional Flask configuration dictionnary
    """

    app = Flask(__name__.split('.')[0])

    # Configuration part
    # Load the default settings
    app.config.from_object(Config)
    # Supercharge from cfg file defined in environment variable
    from_env = app.config.from_envvar('PAMOSE_SETTINGS', silent=False)
    if from_env:
        app.logger.debug('Using settings file %s', os.environ['PAMOSE_SETTINGS'])
    # Supercharge from config parameter
    if config:
        app.config.update(config)  # Extras config parameters

    # Register extras application commands lines
    register_commands(app=app)

    # Register loggers
    register_loggers(app)

    # Register extensions
    register_db(app=app)
    register_schemas(app=app)
    register_ressources(app=app)

    # register_errorhandlers(app)
    # register_shellcontext(app)

    return app


def register_db(app):
    app.logger.debug("Registering database...")
    db.init_app(app=app)


def register_schemas(app):
    app.logger.debug("Registering schemas...")
    ma.init_app(app=app)


def register_ressources(app):
    app.logger.debug("Registering ressources...")
    api.init_app(app)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.initdb)
    app.cli.add_command(commands.tests)
