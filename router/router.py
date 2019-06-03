from ctypes import *
from decimal import Decimal
import math

'''
struct Graph* globalGraph;
extern "C" void inizializeGraph(int V);
extern "C" int findKey(int nodeId);
extern "C" int *findPredecesor(int key);
extern "C" void solve(int start, int ends[],int numEnds);
extern "C" void inicializeEdge(int nodeKey1,int nodeKey2, double cost);
extern "C" int addNode(int nodeKey);'''

class routerc():

    def __init__(self,numNodes):
        self.nodes = {}
        self.vehicles = {}
        self.myrouter = cdll.LoadLibrary('./router/dijkstraListCFile2.so')
        #void inizializeGraph(int V);
        self.myrouter.inizializeGraph.restype = None
        self.myrouter.inizializeGraph.argtypes = [c_int]
        #int findPredecesor(int nodeId);
        self.myrouter.findKey.argtypes = [c_int]
        self.myrouter.findKey.restype = c_int
        #int findPredecesor(int nodeId);
        self.myrouter.findPredecesor.argtypes = [c_int,c_int]
        self.myrouter.findPredecesor.restype = POINTER(c_int)
        #findPredecesorValues
        self.myrouter.findPredecesorValues.argtypes = [c_int,c_int]
        self.myrouter.findPredecesorValues.restype = POINTER(c_double)
        #void solve(int start, int ends[],int numEnds);
        self.myrouter.solve.argtypes = [c_int,c_int]
        self.myrouter.solve.restype = None
        #void inicializeEdge(int nodeKey1,int nodeKey2, double cost)
        self.myrouter.inicializeEdge.argtypes = [c_int,c_int,c_double,c_double,c_double,c_double,c_double,c_double,c_double]
        self.myrouter.inicializeEdge.restype = None
        #int addNode(int nodeKey);
        self.myrouter.addNode.argtypes = [c_int]
        self.myrouter.addNode.restype = c_int
        #void addVehicle(int type, intnode)
        self.myrouter.addVehicle.argtypes = [c_int,c_int]
        self.myrouter.addVehicle.restype = None
        #double getMaxValue()
        self.myrouter.getMaxValue.argtypes = []
        self.myrouter.getMaxValue.restype = c_double
        self.myrouter.inizializeGraph(numNodes)

    def getMaxValue(self):
        return self.myrouter.getMaxValue()

    def addVehicle(self, type, node):
        self.myrouter.addVehicle(type, node)

    #extern "C" int findKey(int nodeId);
    def findKey(self,nodeId):
        return self.myrouter.findKey(nodeId)

    #extern "C" int *findPredecesor(int key);
    def findPredecesor(self,key,vehicle):
        predecesor=self.myrouter.findPredecesor(key,vehicle)
        return predecesor[0], predecesor[1], predecesor[2]

    #extern "C" void solve(int start, int ends[],int numEnds);
    def solve(self,start, ends):
        self.myrouter.solve(start,0)
        self.myrouter.solve(start,1)
        self.myrouter.solve(start,2)
        self.myrouter.solve(start,3)

    #extern "C" void inicializeEdge(int nodeKey1,int nodeKey2, double cost);
    def inicializeEdge(self,nodeKey1, nodeKey2, walkingCost,CarCost,BRPCost,AllTerrainCost,
                       rampPos,rampNeg,dist):
        self.myrouter.inicializeEdge(nodeKey1, nodeKey2, c_double(walkingCost),c_double(CarCost),c_double(BRPCost),c_double(AllTerrainCost),
                                     c_double(rampPos), c_double(rampNeg), c_double(dist))

    #extern "C" int addNode(int nodeKey);
    def addNode(self,nodeKey,lat,lon):
        self.nodes[nodeKey] = {
            "key":self.myrouter.addNode(nodeKey),
            "coor":(Decimal(lat), Decimal(lon))
        }
        return self.nodes[nodeKey]["key"]

    def getKey(self,nodeKey):
        return self.nodes[nodeKey]["key"]

    def returnNodes(self):
        return self.nodes

    def getNearestNode(self,lat,lon):
        minDist=9999
        for node in self.nodes:
            nodeDist=self.distance(self.nodes[node]["coor"],(Decimal(lat),Decimal(lon)))
            if(nodeDist<minDist):
                minDist=nodeDist
                nearestNode=node
        return nearestNode

    def getRoute(self,end,start,vehicle):
        vehiclesSTR=['walk','car','BRP','4x4']
        route = [{
            'coordinates':[float(self.nodes[end]['coor'][0]),float(self.nodes[end]['coor'][1])],
            'point':end
        }]
        predecesor = self.myrouter.findPredecesor(self.nodes[end]['key'], vehicle)
        values = self.myrouter.findPredecesorValues(self.nodes[end]['key'], predecesor[2])
        key, j,vehicle = predecesor[0],predecesor[1],predecesor[2]
        #print(str(predecesor[0])+" "+str(predecesor[1])+" "+str(predecesor[2]))
        rampPos, rampNeg, dist = values[0],values[1],values[2]
        route.append({
            'coordinates':[float(self.nodes[j]['coor'][0]),float(self.nodes[j]['coor'][1])],
            'point':j,
            'vehicle':vehiclesSTR[vehicle],
            'posRamp':rampPos,
            'negRamp':rampNeg,
            'dist':dist
        })
        #print('arriva2')
        while j != start:

            predecesor = self.myrouter.findPredecesor(key, vehicle)
            values = self.myrouter.findPredecesorValues(key, vehicle)
            #print(str(j))
            key, j, vehicle = predecesor[0], predecesor[1], predecesor[2]
            rampPos, rampNeg, dist = values[0], values[1], values[2]
            #print(str(j))
            route.append({
                'coordinates': [float(self.nodes[j]['coor'][0]), float(self.nodes[j]['coor'][1])],
                'point': j,
                'vehicle': vehiclesSTR[vehicle],
                'posRamp': rampPos,
                'negRamp': rampNeg,
                'dist': dist
            })
        return route

    def distance(self, n1, n2):

        lat1, lon1 = n1
        lat2, lon2 = n2
        R=6371000                               # radius of Earth in meters
        phi_1=math.radians(lat1)
        phi_2=math.radians(lat2)

        delta_phi=math.radians(lat2-lat1)
        delta_lambda=math.radians(lon2-lon1)

        a=math.sin(delta_phi/2.0)**2+\
           math.cos(phi_1)*math.cos(phi_2)*\
           math.sin(delta_lambda/2.0)**2
        c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

        return R*c                         # output distance in meters




