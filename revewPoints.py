from VehiclesHandeler import vehicles
from MapHandeler import MapHandeler

mapHandeler=MapHandeler()

graphMultimodal, graphUnimodal = mapHandeler.read_graph("maps/connexioGRAPH2.osm",3007,vehicles)

nodes=[]
nodes.append(graphMultimodal.getNearestNode(41.610400, 1.846006))
nodes.append(graphMultimodal.getNearestNode(41.569510, 1.798772))
nodes.append(graphMultimodal.getNearestNode(41.563525,1.8149363))
nodes.append(graphMultimodal.getNearestNode(41.615415, 1.792733))
print(nodes)