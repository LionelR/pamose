"""
The publicly exposed ressources
"""

from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, Api
from flask import request
from . import models, schemas

api = Api()


def make_response(result=None, feedback=None, issues=None):
    # Alignak response format
    # alignak-module-ws/docs/source/04_services/05-host-report.rst
    # Response to POST on login:
    # {
    #   '_status': 'OK',
    #   '_result': ['the_result']
    # }
    # On error:
    # {'_status': 'ERR', '_issues': ['Access denied.']}
    # Response to PATCH on host:
    # {
    #   '_status': 'OK',
    #   '_feedback': {
    #       'key1': 'value1',
    #       'key2': 'value2',
    #   }
    # }
    # On error
    # {'_status': 'ERR', '_result': '', '_issues': ['Missing targeted element.']}  # like CRITICAL

    status = 'OK'
    if issues:
        status = 'ERR'

    response = {'_status': status}

    if result:
        response['_result'] = [result]  # TODO: Remove list
    if feedback:
        response['_feedback'] = feedback  # Todo: Remove feedback and use result
    if issues:
        response['_issues'] = issues
    return response


class MetricTypeResource(Resource):

    def get(self, id):
        data = models.MetricType.query.filter_by(id=id).first()
        if not data:
            return make_response(issues='Not found'), 404
        schema = schemas.MetricTypeSchema()
        json = schema.dump(obj=data).data
        return make_response(feedback=json), 200


class MetricTypeListResource(Resource):

    def get(self):
        datas = models.MetricType.query.all()
        schema = schemas.MetricTypeSchema(many=True)
        # json = schema.jsonify(obj=datas)
        json = schema.dump(obj=datas).data
        return make_response(feedback=json), 200

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return make_response(issues='No input data provided'), 400

        # Validate and deserialize input
        schema = schemas.MetricTypeSchema()
        data, issues = schema.load(json_data)
        if issues:
            return make_response(issues=issues), 422

        new = models.MetricType(**json_data)
        try:
            models.db.session.add(new)
            models.db.session.commit()
            result = schema.dump(new).data
        except IntegrityError as err:
            return make_response(issues='Data already in database'), 500
        else:
            return make_response(feedback=result), 201


api.add_resource(MetricTypeResource, '/metrictype/<id>')
api.add_resource(MetricTypeListResource, '/metrictypes')


class UserResource(Resource):

    def get(self):
        datas = models.User.query.all()
        schema = schemas.UserSchema(many=True)
        json = schema.dump(obj=datas).data
        return make_response(feedback=json), 200

    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return make_response(issues='No input data provided'), 400

        # Validate and deserialize input
        schema = schemas.UserSchema()
        data, issues = schema.load(json_data)
        if issues:
            return make_response(issues=issues), 422

        name = data.name
        password = data.password

        auth_user = models.User.query.filter_by(name=name).first()

        if not auth_user:
            return make_response(issues='User not found'), 404

        token = auth_user.token

        return make_response(result=token), 200


api.add_resource(UserResource, '/login')
