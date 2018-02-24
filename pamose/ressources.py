"""
The publicly exposed ressources
"""

from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, Api
from flask import request
from . import models, schemas

api = Api()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = models.User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = models.User.query.filter_by(name=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    # g.user = user
    return user


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

    @auth.login_required
    def post(self):
        """
        Create a new user
        :return:
        """
        json_data = request.get_json(force=True)
        if not json_data:
            return make_response(issues='No input data provided'), 400

        username = json_data.get('name', None)
        password = json_data.get('password', None)
        if username is None or password is None:
            return make_response(issues='Not enough input data provided'), 400

        if models.User.query.filter_by(username=username).first() is not None:
            return make_response(issues='Existing user'), 400

        user = models.User(username=username)
        user.hash_password(password)  # Hash and set password_hash in db
        models.db.session.add(user)
        models.db.session.commit()

        return make_response(feedback={'name': user.name}), 201  # , {'Location': url_for('get_user',
                                                                         # id=user.id, _external=True)}


api.add_resource(UserResource, '/user')


class LoginRessource(Resource):

    # @auth.login_required
    def post(self):
        """
        Request a new token
        :return:
        """
        json_data = request.get_json(force=True)
        if not json_data:
            return make_response(issues='No input data provided'), 400

        username = json_data.get('name', None)
        password = json_data.get('password', None)

        auth_user = verify_password(username_or_token=username, password=password)
        if auth_user:
            token = auth_user.generate_auth_token()
            return make_response(result=token.decode('ascii')), 200
        else:
            return make_response(issues="No accepted credentials"), 400


api.add_resource(LoginRessource, '/login')

