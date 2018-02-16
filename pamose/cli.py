"""Click commands."""
import os
import sys
import click
from .settings import ProdConfig, DevConfig
from .app import create_app

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')

MODES = {'dev': DevConfig,
         'prod': ProdConfig}


@click.command()
@click.option('--mode', default='dev', help='Start in "dev" or "prod" mode')
@click.option('--init', is_flag=True, help='Insert initial datas in database. Use it only at really first launch')
def run(mode, init):
    config = MODES.get(mode, None)
    if not config:
        print("You can only use dev or prod for config mode")
        sys.exit(1)
    app = create_app(config_object=config)
    app.run()  # use_reloader=False

    if init:
        from .initializer import insert_datas
        insert_datas(app=app)


@click.command()
def test():
    """Run the tests."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    exit(rv)
