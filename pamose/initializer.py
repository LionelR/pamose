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


def insert_datas(app):
    """
    Insert initial datas suitable for usage
    """
    app.logger.debug("Inserting initial datas...")

    with app.app_context():
        for table, datas in INITIAL_TABLES.items():
            for data in datas:
                t = table(**data)
                models.db.session.add(t)

        models.db.session.commit()
