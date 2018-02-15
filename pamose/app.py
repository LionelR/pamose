"""
The app module, containing the app factory function.
"""

import os
from flask import Flask

from pamose.models import register as register_db
from pamose.schemas import register as register_schemas
from pamose.loggers import register as register_loggers


def create_app(config_object):
    """
    The Flask Application creating function
    :param config_object: The configuration object to use.
    """
    #  An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    # app.config.from_envvar('PAMOSE_SETTINGS')
    register_db(app)
    register_schemas(app)
    # register_loggers(app)

    # register_errorhandlers(app)
    # register_shellcontext(app)
    return app


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

#
# def register_shellcontext(app):
#     """Register shell context objects."""
#     from pamose import models
#     def shell_context():
#         """Shell context objects."""
#         return {
#             'db': db,
#             'User': models.User}
#
#     app.shell_context_processor(shell_context)

