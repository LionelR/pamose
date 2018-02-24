"""
Database models definitions
"""

import time
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

db = SQLAlchemy()

# Many-to-many secondary (central) tables definition
user_usergroup_table = db.Table('user_usergroup',
                                db.Model.metadata,
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                db.Column('user_group_id', db.Integer, db.ForeignKey('user_group.id'), primary_key=True)
                                )

role_right_table = db.Table('role_right',
                            db.Model.metadata,
                            db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
                            db.Column('right_id', db.Integer, db.ForeignKey('right.id'), primary_key=True)
                            )

entity_tag_table = db.Table('entity_tag',
                            db.Model.metadata,
                            db.Column('entity_id', db.Integer, db.ForeignKey('entity.id'), primary_key=True),
                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                            )


class User(db.Model):
    """
    Users able to connect and perform actions in the database
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=True)  # Will be completed by self.hash_password after user instanciation
    token = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users', lazy=True)
    user_groups = db.relationship('UserGroup', secondary=user_usergroup_table, backref='users', lazy=True)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class UserGroup(db.Model):
    """
    Users groups
    """
    __tablename__ = 'user_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class Role(db.Model):
    """
    Users roles (admin, anonymous, ...)
    """
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    rights = db.relationship('Right', secondary=role_right_table, backref='roles', lazy=True)


class Right(db.Model):
    """
    Description of roles rights (CRUD)
    """
    __tablename__ = 'right'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class Entity(db.Model):
    """
    Central table for describing the logical hierarchy of monitored objects
    """
    __tablename__ = 'entity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    alias = db.Column(db.String, nullable=True)
    tags = db.relationship('Tag', secondary=entity_tag_table, backref='entities', lazy=True)
    entity_type_id = db.Column(db.Integer, db.ForeignKey('entity_type.id'))
    entity_type = db.relationship("EntityType", backref='entities')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')  # , backref='entities', lazy=True)
    parent_entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'))
    # parent = db.relationship("Entity", remote_side=[id])
    childs = db.relationship("Entity", backref=db.backref('parent', remote_side=[id]))
    livestates = db.relationship('Livestate', backref='entity', lazy=True)
    is_auto_acknowledge = db.Column(db.Boolean, nullable=False, default=False)
    is_template = db.Column(db.Boolean, nullable=False, default=False)
    is_activated = db.Column(db.Boolean, nullable=False, default=False)
    is_auto_expirable = db.Column(db.Boolean, nullable=False, default=True)
    auto_expirable_interval = db.Column(db.Integer, nullable=False, default=0)


class State(db.Model):
    """
    List of possible states (EXPIRED, OK, UP, DOWN, ...) by Entity Type
    """
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    severity_id = db.Column(db.Integer, db.ForeignKey('severity.id'))
    severity = db.relationship("Severity", backref='states')
    entity_type_id = db.Column(db.Integer, db.ForeignKey('entity_type.id'))
    entity_type = db.relationship("EntityType", backref='states')


class Severity(db.Model):
    """
    States severities levels
    """
    __tablename__ = 'severity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    value = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String, unique=False, nullable=True)


class Tag(db.Model):
    """
    Available tags
    """
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class EntityType(db.Model):
    """
    List of entities types (Realm, Host, Service, ...)
    """
    __tablename__ = 'entity_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


class Livestate(db.Model):
    """
    For storing entities livestates
    """
    __tablename__ = 'livestate'
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State', backref='livestates', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')  # , backref='livestates', lazy=True)
    timestamp = db.Column(db.DateTime, default=time.time())
    output = db.Column(db.String, unique=False, nullable=True)
    longoutput = db.Column(db.String, unique=False, nullable=True)
    is_acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    metrics = db.relationship('Metric', backref='livestate', lazy=True)


class Metric(db.Model):
    """
    For storing livestates metrics
    """
    __tablename__ = 'metric'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=time.time())
    name = db.Column(db.String, unique=False, nullable=False)
    value = db.Column(db.Float, unique=False, nullable=True)
    livestate_id = db.Column(db.Integer, db.ForeignKey('livestate.id'))
    metric_type_id = db.Column(db.Integer, db.ForeignKey('metric_type.id'))
    metric_type = db.relationship('MetricType', backref='metrics', lazy=True)


class MetricType(db.Model):
    """
    Possible metric type (value or cumulative)
    """
    __tablename__ = 'metric_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=False, nullable=True)


INITIAL_TABLES = {
    MetricType: [
        {'name': 'scalaire', 'description': 'Valeur indépendante et fluctuante'},
        {'name': 'cumulative', 'description': 'Valeur qui se cumule dans le temps'},
        {'name': 'delta', 'description': 'Différence entre deux valeurs cumulatives'},
    ],
    EntityType: [
        {'name': 'realm'},
        {'name': 'host'},
        {'name': 'service'},
    ],
    Tag: [
        {'name': 'Applications'},
        {'name': 'Global'},
        {'name': 'Logiciels'},
        {'name': 'Périphériques'},
        {'name': 'Services'},
    ],
    Severity: [
        {'name': 'NOTHING', 'description': 'Sans gravité', 'value': 0},
        {'name': 'LOW', 'description': 'Sévérité basse', 'value': 1},
        {'name': 'MEDIUM', 'description': 'Sévérité moyenne', 'value': 2},
        {'name': 'HIGH', 'description': 'Sévérité grave', 'value': 3},
    ],
    Right: [
        {'name': 'create'},
        {'name': 'read'},
        {'name': 'update'},
        {'name': 'delete'},
    ],
    UserGroup: [
        {'name': 'admin'},
        {'name': 'reader'},
        {'name': 'borne'},
    ],
    Role: [
        {'name': 'admin', 'id': 0}
    ],
    User: [
        {'name': 'admin', 'password': 'admin', 'role_id': 0}
    ]
}


