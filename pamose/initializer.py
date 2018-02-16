"""
Initial Datas population
"""

from pamose import models

INITIAL_TABLES = {
    models.MetricType: [
        {'name': 'scalaire', 'description': 'Valeur indépendante et fluctuante'},
        {'name': 'cumulative', 'description': 'Valeur qui se cumule dans le temps'},
        {'name': 'delta', 'description': 'Différence entre deux valeurs cumulatives'},
    ],
    models.EntityType: [
        {'name': 'realm'},
        {'name': 'host'},
        {'name': 'service'},
    ],
    models.Tag: [
        {'name': 'Applications'},
        {'name': 'Global'},
        {'name': 'Logiciels'},
        {'name': 'Périphériques'},
        {'name': 'Services'},
    ],
    models.Severity: [
        {'name': 'NOTHING', 'description': 'Sans gravité', 'value': 0},
        {'name': 'LOW', 'description': 'Sévérité basse', 'value': 1},
        {'name': 'MEDIUM', 'description': 'Sévérité moyenne', 'value': 2},
        {'name': 'HIGH', 'description': 'Sévérité grave', 'value': 3},
    ],
    models.Right: [
        {'name': 'create'},
        {'name': 'read'},
        {'name': 'update'},
        {'name': 'delete'},
    ],
    models.UserGroup: [
        {'name': 'admin'},
        {'name': 'reader'},
        {'name': 'borne'},
    ]
}


def initial_datas(app):
    """
    Prepare and create Tables classes instances with initial values creation, to be commited after the tables are
    first time created
    :param app: the app instance (for logger)
    :return: list. queries to commit for first time datas insertion
    """

    #  From https://stackoverflow.com/questions/30067591/alembic-sqlalchemy-after-create-not-triggering
    def create(param):
        def callee(table, connection, **kwargs):
            app.logger.debug("Creating initial datas for table {0}...".format(table))
            for values in INITIAL_TABLES[param]:
                t = param(**values)
                db.session.add(t)

        return callee

    for table_class in INITIAL_TABLES:
        event.listen(table_class.__table__, 'after_create', create(table_class))

    db.session.commit()