"""
The app module, containing the app factory function.
"""

import click
from flask import Flask

from .models import db
from .schemas import ma
from .ressources import api

from . import commands

from .loggers import register as register_loggers
from .errorhandlers import register as register_errorhandlers
from .shellcontexts import register as register_shellcontexts


def create_app(config_object):
    """
    The Flask Application creating function
    :param config_object: The configuration object to use.
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
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
    # db.create_all(app=app)


def register_schemas(app):
    app.logger.debug("Registering schemas...")
    ma.init_app(app=app)


def register_ressources(app):
    app.logger.debug("Registering ressources...")
    api.init_app(app)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.initdb)
