"""
The publicly exposed ressources
"""
from flask_restful import reqparse, Resource, Api

from pamose import models
from pamose import schemas

api = Api()


class MetricTypeResource(Resource):

    def get(self, id):
        data = models.db.session.query(models.MetricType).filter_by(id=id).first()
        if not data:
            return {'message': 'Not found'}, 404
        return {id: data}


class MetricTypeListResource(Resource):

    def get(self):
        datas = models.MetricType.query.all()
        print(datas)
        return [{data.id: data} for data in datas]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        if not 'name' in args or not 'description' in args:
            return {'message': 'Missing required parameters.'}, 400
        new = models.MetricType(name=args['name'], description=args['description'])
        models.db.session.add(new)
        models.db.session.commit()
        return {new.id: new}, 201


api.add_resource(MetricTypeResource, '/metrictype/<id>')
api.add_resource(MetricTypeListResource, '/metrictypes')


def register(app):
    api.init_app(app)

