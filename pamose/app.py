"""
The app module, containing the app factory function.
"""

from flask import Flask

from .settings import Config, DevConfig
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
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_object(DevConfig)
    app.config.from_envvar('PAMOSE_CONFIG_FILE', silent=True)
    if config:
        app.config.update(config)  # Extras config parameters
    # app.logger.info('Using configuration file %s', app.config['PAMOSE_CONFIG_FILE'])
    register_db(app=app)
    register_schemas(app=app)
    register_ressources(app=app)
    register_commands(app=app)

    # register_loggers(app)
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
