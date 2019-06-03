import os

from flask import Flask,request
from flask_restful import Resource, Api
from flask_restful.utils import cors
from RouteHandeler import RouteHandeler
import json
from flask.views import MethodView
import logging
import time
logging.getLogger('flask_cors').level = logging.DEBUG
app = Flask(__name__)
api = Api(app)
class calculateRoute(Resource):#Resource

    @cors.crossdomain(origin='*')
    def get(self):
        args = request.args
        print(args)  # For debugging
        lat = args['lat']
        lon = args['lon']
        if('vehicles' in args.keys()):
            vehicles=[int(i) for i in args['vehicles'].split(',')]
            #start=graph.getNearestNode('41.60448710003', '1.84747999968')
            return json.dumps(routeHandeler.getRoutesWithMandatory(lat,lon,vehicles))
        else:
            return json.dumps(routeHandeler.getRoutesWithMandatory(lat,lon,[]))


with open('configurationFiles/flaskConfig.json') as json_file:
    configuration_data = json.load(json_file)
#not app.debug or
if  os.environ.get("WERKZEUG_RUN_MAIN") == "true" or configuration_data["debug"] is False:
    timer=time.time()
    routeHandeler=RouteHandeler()
    print('init time')
    print(time.time()-timer)

api.add_resource(calculateRoute, '/calculateRoute')
#http://127.0.0.1:5000/calculateRoute?lat=41.60448710003&lon=1.84747999968
if __name__ == '__main__':
    app.run(debug=configuration_data["debug"],host=configuration_data["host"],port=configuration_data["port"])
