# from http://alexmic.net/flask-sqlalchemy-pytest/

import os
import pytest

from pamose.app import create_app
from pamose.models import db as _db
from pamose import models


TESTDB = 'test_project.db'
TESTDB_PATH = "/tmp/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    config_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    app = create_app(config=config_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    app.logger.debug("Inserting initial datas...")
    for table, datas in models.INITIAL_TABLES.items():
        for data in datas:
            t = table(**data)
            _db.session.add(t)
    _db.session.commit()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


def test_post_model(session):
    realm = models.EntityType(name='Realm')
    host = models.EntityType(name='Host')
    service = models.EntityType(name='Service')

    session.add(realm)
    session.add(host)
    session.add(service)
    session.commit()

    ug = models.UserGroup.query.all()
    print(ug)
    assert len(ug) < 2
    # assert realm.id > 0
