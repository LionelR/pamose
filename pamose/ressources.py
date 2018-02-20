"""
The publicly exposed ressources
"""

from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, Api
from flask import request
from . import models, schemas

api = Api()


class MetricTypeResource(Resource):

    def get(self, id):
        data = models.MetricType.query.filter_by(id=id).first()
        if not data:
            return {'message': 'Not found'}, 404
        schema = schemas.MetricTypeSchema()
        return schema.jsonify(obj=data)


class MetricTypeListResource(Resource):

    def get(self):
        datas = models.MetricType.query.all()
        schema = schemas.MetricTypeSchema(many=True)
        return schema.jsonify(obj=datas)

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400

        # Validate and deserialize input
        schema = schemas.MetricTypeSchema()
        data, errors = schema.load(json_data)
        if errors:
            return errors, 422

        # not_new = models.MetricType.query.filter_by(name=data['name']).first()
        # if not_new:
        #     return {'message': 'MetricType already exists'}, 400

        # category = Category(name=json_data['name'])
        new = models.MetricType(**json_data)

        try:
            models.db.session.add(new)
            models.db.session.commit()
            result = schema.dump(new).data
        except IntegrityError as err:
            return {"status": 'error', 'data': 'Data already in database'}, 500
        else:
            return {"status": 'success', 'data': result}, 201


api.add_resource(MetricTypeResource, '/metrictype/<id>')
api.add_resource(MetricTypeListResource, '/metrictypes')
