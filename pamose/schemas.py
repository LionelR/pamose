"""
Schemas serialisation definitions
"""

# /!\ from https://flask-marshmallow.readthedocs.io/en/latest/,
# Flask-SQLAlchemy (in models) must be initialized before Flask-Marshmallow
from . import models
from flask_marshmallow import Marshmallow

ma = Marshmallow()  # Serialization extension


class UserSchema(ma.ModelSchema):
    class Meta:
        model = models.User


class UserGroupSchema(ma.ModelSchema):
    class Meta:
        model = models.UserGroup


class RoleSchema(ma.ModelSchema):
    class Meta:
        model = models.Role


class RightSchema(ma.ModelSchema):
    class Meta:
        model = models.Right


class EntitySchema(ma.ModelSchema):
    class Meta:
        model = models.Entity


class StateSchema(ma.ModelSchema):
    class Meta:
        model = models.State


class SeveritySchema(ma.ModelSchema):
    class Meta:
        model = models.Severity


class TagSchema(ma.ModelSchema):
    class Meta:
        model = models.Tag


class EntityTypeSchema(ma.ModelSchema):
    class Meta:
        model = models.EntityType


class LivestateSchema(ma.ModelSchema):
    class Meta:
        model = models.Livestate


class MetricSchema(ma.ModelSchema):
    class Meta:
        model = models.Metric


class MetricTypeSchema(ma.ModelSchema):
    class Meta:
        model = models.MetricType
        fields = ('id', 'name', 'description')
