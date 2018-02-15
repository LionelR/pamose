"""
Database models definitions
"""

import time
from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy

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
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users', lazy=True)
    user_groups = db.relationship('UserGroup', secondary=user_usergroup_table, backref='users', lazy=True)


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
    Description of roles rights (write, append, read, ...)
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
    Possible metric type (standard or cumulative)
    """
    __tablename__ = 'metric_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)


def register(app):
    db.init_app(app=app)
    db.create_all(app=app)

    app.logger.info("Inserting Initial Values for Severity")
    event.listen(Severity.__table__, 'after_create', insert_initial_values)


def insert_initial_values(*args, **kwargs):

    for name, value in [('LOW', 0), ('MEDIUM', 1), ('HIGH', 2), ('CRITICAL', 3)]:
        s = Severity(name=name, value=value)
        db.session.add(s)
    db.session.commit()
