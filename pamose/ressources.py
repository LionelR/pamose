"""
The publicly exposed ressources
"""

import datetime as dt

from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, Api
from flask import request, current_app
from . import models, schemas

api = Api()
auth = HTTPBasicAuth()


# @auth.verify_token
@auth.verify_password
def verify_token(token, password):
    """
    Defines the auth mechanism used by subsequent login_required decorator
    :param token: str. Token to verify
    :return: bool.
    """
    verified = models.User.verify_token(token=token.encode('UTF-8'))
    return verified


def make_response(result=None, feedback=None, issues=None):
    """
    Returns a well formated response (dict/JSON style) to be used in Flask Response, as it is in Alignak
    :param result: The unique result to return (be set in a list)
    :param feedback: Informations to return to the client
    :param issues: Message error
    :return: dict
    """
    # TODO: reformat that in the future
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
        response['_result'] = result  # TODO: Remove list
    if feedback:
        response['_feedback'] = feedback  # Todo: Remove feedback and use result
    if issues:
        response['_issues'] = issues
    return response


def flush(rec):
    """
    FLush (commit) the record in the database
    :param rec: db.record
    :return: Nothing
    """
    models.db.session.add(rec)
    models.db.session.commit()


class LoginRessource(Resource):

    def post(self):
        """
        Request a new token
        :return:
        """
        post_data = request.get_json()
        if not post_data:
            return make_response(issues='No enought data provided'), 400

        username = post_data.get('username', None)
        password = post_data.get('password', None)
        if username is None or password is None:
            return make_response(issues='No enought data provided'), 400

        user = models.User.query.filter_by(name=username).first()
        if user is None or not user.verify_password(password=password):
            return make_response(issues='Bad credentials'), 400

        token = user.new_token()

        return make_response(result=token.decode('UTF-8')), 200


api.add_resource(LoginRessource, '/login')


class MetricTypeResource(Resource):

    @auth.login_required
    def get(self, id):
        data = models.MetricType.query.filter_by(id=id).first()
        if not data:
            return make_response(issues='Not found'), 404
        schema = schemas.MetricTypeSchema()
        json = schema.dump(obj=data).data
        return make_response(feedback=json), 200


class MetricTypeListResource(Resource):

    @auth.login_required
    def get(self):
        datas = models.MetricType.query.all()
        schema = schemas.MetricTypeSchema(many=True)
        # json = schema.jsonify(obj=datas)
        json = schema.dump(obj=datas).data
        return make_response(feedback=json), 200

    @auth.login_required
    def post(self):
        post_data = request.get_json(force=True)
        if not post_data:
            return make_response(issues='No input data provided'), 400

        # Validate and deserialize input
        schema = schemas.MetricTypeSchema()
        data, issues = schema.load(post_data)
        if issues:
            return make_response(issues=issues), 422

        new = models.MetricType(**post_data)
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
        post_data = request.get_json(force=True)
        if not post_data:
            return make_response(issues='No input data provided'), 400

        username = post_data.get('name', None)
        password = post_data.get('password', None)
        if username is None or password is None:
            return make_response(issues='Not enough input data provided'), 400

        if models.User.query.filter_by(username=username).first() is not None:
            return make_response(issues='Existing user'), 400

        user = models.User(name=username)
        user.set_password_hash(password)  # Hash and set password in User instance
        models.db.session.add(user)
        models.db.session.commit()

        return make_response(feedback={'name': user.name}), 201  # , {'Location': url_for('get_user',
        # id=user.id, _external=True)}


api.add_resource(UserResource, '/user')


class HostRessource(Resource):
    """
    Used to create/update an host and its services/metrics

    An host is in a Realm.
    If no realm is provided, fallback to the logged-in user's realm
    TODO: realm is replaced by another one


    Always returns the basic informations for the host:
        check_interval
        freshness_threshold
        passive_check_enabled
        active_check_enabled

    Requested format:

    name: _HOSTNAME_
    active_checks_enabled: false
    passive_checks_enabled: true
    template:
        _realm: simulation
        _sub_realm: False
        alias: _HOSTNAME_
        _templates:
          - olympia-cb
    livestate:
        timestamp: _TIMESTAMP_
        state: UP
        output: _HOSTOUTPUT_
        long_output: I am a simulated host
    services: [_SERVICES__]
        service:
            name: _SERVICENAME_
            active_checks_enabled: false
            passive_checks_enabled: true
            livestate:
                timestamp: _TIMESTAMP_
                state: OK
                output: Simulated Service
                perf_data: _PERFDATA_

    """

    @auth.login_required
    def patch(self):
        json_data = request.get_json()
        if not json_data:
            return make_response(issues='No input data provided'), 400

        host_name = json_data.get('name')
        is_monitored = json_data.get('passive_checks_enabled', False)

        # Host get/create
        rec_entity_host = models.Entity.query.filter_by(name=host_name).first()
        if not rec_entity_host:  # Create it
            # Realm get/create
            template = json_data.get('template', None)  # TODO: Better solution for realm info retrieving
            realm_name = template.get('_realm', None)
            # host_templates = template.get('_templates', None)  # TODO: Define templates
            rec_entity_realm = models.Entity.query.filter_by(name=realm_name).first()
            if not rec_entity_realm:  # Create it
                default_realm = models.Entity.query.get(0)
                rec_entity_realm = models.Entity(name=realm_name,
                                                 parent_entity_id=default_realm.id,
                                                 entity_type_id=models.EntityType.query.filter_by(
                                                     name='realm').first().id
                                                 )
                flush(rec_entity_realm)

            rec_entity_host = models.Entity(name=host_name,
                                            parent_entity_id=rec_entity_realm.id,
                                            entity_type_id=models.EntityType.query.filter_by(name='host').first().id,
                                            is_monitored=is_monitored
                                            )
            flush(rec_entity_host)

        # Host Livestate create
        livestate = json_data.get('livestate', None)
        if livestate:
            rec_livestate = insert_livestate(entity_parent=rec_entity_host, livestate=livestate)

            # Metric create
            raw_metrics = livestate.get('perf_data', None)
            if raw_metrics:
                insert_metrics(entity_livestate=rec_livestate, raw_metrics=raw_metrics)

        # Services get/create
        services = json_data.get('services', None)
        current_app.logger.debug("services: {0}".format(services))
        if services:
            for service in services:
                service_name = service.get('name', None)
                service_name = "{0}||{1}".format(host_name, service_name)  # For uniqueness
                is_monitored = service.get('passive_checks_enabled', False)

                rec_entity_service = models.Entity.query.filter_by(name=service_name).first()
                if not rec_entity_service:  # Create it
                    rec_entity_service = models.Entity(name=service_name,
                                                       parent_entity_id=rec_entity_host.id,
                                                       entity_type_id=models.EntityType.query.filter_by(
                                                           name='service').first().id,
                                                       is_monitored=is_monitored
                                                       )
                    flush(rec_entity_service)

                # Service Livestate create
                livestate = service.get('livestate', None)
                if livestate:
                    rec_livestate = insert_livestate(entity_parent=rec_entity_service, livestate=livestate)

                    # Metric create
                    raw_metrics = livestate.get('perf_data', None)
                    if raw_metrics:
                        insert_metrics(entity_livestate=rec_livestate, raw_metrics=raw_metrics)

        models.db.session.commit()

        feedback = {
            'check_interval': rec_entity_host.checkall_interval,
            'freshness_threshold': rec_entity_host.heartbeat_interval,
            'passive_check_enabled': rec_entity_host.is_monitored,
            'active_check_enabled': False
        }
        return make_response(feedback=feedback), 200


api.add_resource(HostRessource, '/host')


def insert_livestate(entity_parent, livestate):
    """
    Insert a Livestate in DB for an parent entity
    :param entity_parent: models.Entity (Host or Service)
    :param livestate: dict. The livestate to insert
    :return: models.Livestate
    """
    timestamp = livestate.get('timestamp', dt.datetime.now().timestamp())
    state = livestate.get('state')
    output = livestate.get('output')
    long_output = livestate.get('long_output')

    entity_state = models.State.query.filter_by(name=state).first()
    rec_livestate = models.Livestate(
        timestamp=dt.datetime.fromtimestamp(timestamp),
        output=output,
        long_output=long_output,
        entity_id=entity_parent.id,
        state_id=entity_state.id,
        is_acknowledged=entity_parent.is_auto_acknowledge
    )
    flush(rec_livestate)
    return rec_livestate


def insert_metrics(entity_livestate, raw_metrics):
    """
    Insert Metrics in DB
    :param entity_livestate: models.Livestate. Livestate instance
    :param raw_metrics: str. Metrics in raw format
        raw_metrics (perf_data) format: "'metric1_name'=metric1_value(c) 'metric2_name'= metric2_value(c)..."
        if value ends with 'c', then it's cumulative, else raw value
    :return: Nothing
    """

    to_flush = False
    for raw_metric in raw_metrics.strip().split(' '):
        name, value = raw_metric.split('=')
        if value.endswith('c'):
            value = value[:-1].replace("'", "")
            entity_metric_type = models.MetricType.query.filter_by(name='cumulative').first()
        else:
            entity_metric_type = models.MetricType.query.filter_by(name='raw').first()

        rec_metric = models.Metric(
            timestamp=entity_livestate.timestamp,
            name=name,
            value=float(value),
            livestate_id=entity_livestate.id,
            metric_type_id=entity_metric_type.id
        )
        models.db.session.add(rec_metric)
        to_flush = True

    if to_flush:
        models.db.session.commit()
