"""
Extras click commands
"""

import os

import click
from flask import current_app
from flask.cli import with_appcontext

from . import models

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
@with_appcontext
def initdb():
    """
    Initialize the database (should be runs once)
    """
    current_app.logger.debug("Creating database...")
    models.db.create_all(app=current_app)

    current_app.logger.debug("Inserting initial datas...")
    with current_app.app_context():
        for table, datas in models.INITIAL_TABLES.items():
            if table is models.User:
                for data in datas:
                    password = data.pop('password')
                    user = models.User(**data)
                    user.set_password_hash(password=password)
                    models.db.session.add(user)
            else:
                for data in datas:
                    t = table(**data)
                    models.db.session.add(t)

        models.db.session.commit()


@click.command()
@with_appcontext
def tests():
    """Run the tests."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)
