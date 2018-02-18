"""Click commands."""
import os
import click
from flask.cli import FlaskGroup


def create_flask_app(info):
    from .app import create_app
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_flask_app)
def cli():
    """This is the main Pamose command-line"""


if __name__ == '__main__':
    cli()
