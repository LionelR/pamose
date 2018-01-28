# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask  # , render_template

from pamose import cli, models
from .extensions import db
from .settings import ProdConfig


def create_app(config_object=ProdConfig):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    # register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    return None


# def register_errorhandlers(app):
#     """Register error handlers."""
#     def render_error(error):
#         """Render error template."""
#         # If a HTTPException, pull the `code` attribute; default to 500
#         error_code = getattr(error, 'code', 500)
#         return render_template('{0}.html'.format(error_code)), error_code
#     for errcode in [401, 404, 500]:
#         app.errorhandler(errcode)(render_error)
#     return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(cli.test)
    app.cli.add_command(cli.lint)
    app.cli.add_command(cli.clean)
    app.cli.add_command(cli.urls)
