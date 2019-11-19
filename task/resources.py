from flask_restful import Resource


class HelloGeek(Resource):
    def get(self):
        return {'test': "test"}
