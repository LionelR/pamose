"""
Extras click commands
"""

import click
from flask import current_app
from flask.cli import with_appcontext

from . import models


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
            for data in datas:
                t = table(**data)
                models.db.session.add(t)

        models.db.session.commit()
