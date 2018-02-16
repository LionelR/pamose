"""
The app module, containing the app factory function.
"""

from flask import Flask

from pamose.models import register as register_db
from pamose.schemas import register as register_schemas
from pamose.api import register as register_api
from pamose.loggers import register as register_loggers
from pamose.errorhandlers import register as register_errorhandlers
from pamose.shellcontexts import register as register_shellcontexts


def create_app(config_object):
    """
    The Flask Application creating function
    :param config_object: The configuration object to use.
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_db(app)
    register_api(app)
    # register_schemas(app)
    # register_loggers(app)
    # register_errorhandlers(app)
    # register_shellcontext(app)

    return app
