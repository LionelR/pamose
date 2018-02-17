"""Click commands."""
import os
import click
from flask.cli import FlaskGroup
from .settings import ProdConfig, DevConfig


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')

MODES = {'dev': DevConfig,
         'prod': ProdConfig}


def create_flask_app(info):
    from .app import create_app
    config = DevConfig
    return create_app(config_object=config)


@click.group(cls=FlaskGroup, create_app=create_flask_app)
def cli():
    """This is the main Pamose command-line"""


if __name__ == '__main__':
    cli()
