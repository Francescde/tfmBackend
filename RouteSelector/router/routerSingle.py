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
        self.nodesInv = {}
        self.myrouter = cdll.LoadLibrary('./RouteSelector/router/dijkstraListCFile3.so')
        #void inizializeGraph(int V);
        self.myrouter.inizializeGraph.restype = None
        self.myrouter.inizializeGraph.argtypes = [c_int]
        #int findPredecesor(int nodeId);
        self.myrouter.findKey.argtypes = [c_longlong]
        self.myrouter.findKey.restype = c_int
        #int findPredecesor(int nodeId);
        self.myrouter.findPredecesor.argtypes = [c_int,c_int]
        self.myrouter.findPredecesor.restype = POINTER(c_longlong)
        #findPredecesorValues
        self.myrouter.findPredecesorValues.argtypes = [c_int,c_int]
        self.myrouter.findPredecesorValues.restype = POINTER(c_double)
        #void solve(int start, int ends[],int numEnds);
        self.myrouter.solve.argtypes = [c_longlong,c_int]
        self.myrouter.solve.restype = None
        #void inicializeEdge(int nodeKey1,int nodeKey2, double cost)
        self.myrouter.inicializeEdge.argtypes = [c_int,c_int,c_double,c_double,c_double,c_double,c_double,c_double,c_double]
        self.myrouter.inicializeEdge.restype = None
        #int addNode(int nodeKey);
        self.myrouter.addNode.argtypes = [c_longlong]
        self.myrouter.addNode.restype = c_int
        #void addVehicle(int type, intnode)
        self.myrouter.addVehicle.argtypes = [c_int,c_int]
        self.myrouter.addVehicle.restype = None
        #double getMaxValue()
        self.myrouter.getMaxValue.argtypes = []
        self.myrouter.getMaxValue.restype = c_double
        #extern "C" double *costValuesOfNode( node src, node dest);
        self.myrouter.costValuesOfNode.argtypes = [c_int,c_int]
        self.myrouter.costValuesOfNode.restype = POINTER(c_double)
        #extern "C" void addfinal(int nodeKey);
        self.myrouter.addfinal.argtypes = [c_int]
        self.myrouter.addfinal.restype = None
        self.myrouter.inizializeGraph(numNodes)

    def costValuesOfNode(self,src,dest):
        return self.myrouter.costValuesOfNode(src,dest)

    def addfinal(self,key):
        self.myrouter.addfinal(self.nodesInv[key])


    def getValuesOfNodeAsDict(self,src,dest):
        valuesCost=self.costValuesOfNode(src,dest)
        weights = {
            "walk": valuesCost[0],
            "car": valuesCost[1],
            "BRP": valuesCost[2],
            "4x4": valuesCost[3]
        }
        return weights

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
    def solve(self,start, vehicle):
        self.myrouter.solve(start,vehicle)

    #extern "C" void inicializeEdge(int nodeKey1,int nodeKey2, double cost);
    def inicializeEdge(self,nodeKey1, nodeKey2, walkingCost,CarCost,BRPCost,AllTerrainCost,
                       rampPos,rampNeg,dist):
        self.myrouter.inicializeEdge(self.nodesInv[nodeKey1],self.nodesInv[nodeKey2], c_double(walkingCost),c_double(CarCost),c_double(BRPCost),c_double(AllTerrainCost),
                                     c_double(rampPos), c_double(rampNeg), c_double(dist))

    #extern "C" int addNode(int nodeKey);
    def addNode(self,nodeKey,lat,lon):
        newkey=self.myrouter.addNode(nodeKey)
        self.nodes[newkey] = {
            "key":nodeKey,
            "coor":(Decimal(lat), Decimal(lon))
        }
        self.nodesInv[nodeKey]=newkey;
        return newkey

    def getKey(self,nodeKey):
        for key in self.nodes.keys():
            if self.nodes[key]['key']==nodeKey:
                return key
        return nodeKey

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

    def getAllPredecesors(self,vehicle):
        predecesors = []
        for end in self.nodes.keys():
            predecesorv=self.myrouter.findPredecesor(end, vehicle)
            ownkey, key, vehicleUse = predecesorv[0],predecesorv[1],predecesorv[2]
            if(ownkey>=0):
                values = self.myrouter.findPredecesorValues(end, vehicle)
                rampPos, rampNeg, dist, cost = values[0],values[1],values[2],values[3]
                if(values[4+vehicle]<9999):
                    obj = {
                        'from': self.nodes[end]["key"],
                        'to': self.nodes[ownkey]["key"],
                        'vehicle': vehicle,
                        'posRamp': rampPos,
                        'negRamp': rampNeg,
                        'dist': dist,
                        'cost': cost,
                        'costu': {
                            "walk": values[4],
                            "car": values[5],
                            "BRP": values[6],
                            "4x4": values[7]
                        }
                    }
                    predecesors.append(obj)
        return predecesors

    def getUnexplored(self,start):
        predecesors={}
        for vehicle in [0,1,2,3]:
            self.solve(start, vehicle)
            predecesors[vehicle] = []
            for end in self.nodes.keys():
                predecesorv=self.myrouter.findPredecesor(end, vehicle)
                ownkey, key, vehicleUse = predecesorv[0],predecesorv[1],predecesorv[2]
                if(ownkey<0 and not self.nodes[end]["key"]==start):
                    predecesors[vehicle].append(self.nodes[end]["key"])
        predecesorsList=[]
        for pre in predecesors[0]:
            if (pre in predecesors[1] and pre in predecesors[2] and pre in predecesors[3]):
                predecesorsList.append(pre)
        return predecesorsList

    def getAllPredecesors(self,vehicle,final):
        predecesors = {}
        for end in self.nodes.keys():
            predecesorv=self.myrouter.findPredecesor(end, vehicle)
            ownkey, key, vehicleUse = predecesorv[0],predecesorv[1],predecesorv[2]
            if(ownkey>=0):
                predecesors[end]=[ownkey]
                while( final != self.nodes[ownkey]["key"]):
                    predecesorv=self.myrouter.findPredecesor(end, vehicle)
                    ownkey, key, vehicleUse = predecesorv[0],predecesorv[1],predecesorv[2]
                    predecesors[end].append(ownkey)
        return predecesors


    def getRoute(self,end,start,vehicle):
        vehiclesSTR=['walk','car','BRP','4x4']
        #print('predecesor')
        predecesor = self.myrouter.findPredecesor(self.nodesInv[end], vehicle)
        #print(end,predecesor[0],predecesor[1],predecesor[2])
        values = self.myrouter.findPredecesorValues(self.nodesInv[end], vehicle)
        #print('data found')
        #print(str(predecesor[0])+" "+str(predecesor[1])+" "+str(predecesor[2]))
        rampPos, rampNeg, dist, cost = values[0],values[1],values[2],values[3]
        route = [{
            'coordinates':[float(self.nodes[self.nodesInv[end]]['coor'][0]),float(self.nodes[self.nodesInv[end]]['coor'][1])],
            'point':end,
            'posRamp':rampPos,
            'negRamp':rampNeg,
            'dist':dist,
            'cost':cost,
            'costs': {
                "walk": values[4],
                "car": values[5],
                "BRP": values[6],
                "4x4": values[7]
            }
        }]
        predecesor = self.myrouter.findPredecesor(self.nodesInv[end], vehicle)
        values = self.myrouter.findPredecesorValues(self.nodesInv[end], vehicle)
        key, j,vehicle = predecesor[0],predecesor[1],predecesor[2]
        #print(str(predecesor[0])+" "+str(predecesor[1])+" "+str(predecesor[2]))
        rampPos, rampNeg, dist, cost = values[0],values[1],values[2],values[3]
        route.append({
            'coordinates':[float(self.nodes[key]['coor'][0]),float(self.nodes[key]['coor'][1])],
            'point':key,
            'vehicle':vehiclesSTR[vehicle],
            'posRamp':rampPos,
            'negRamp':rampNeg,
            'dist':dist,
            'cost':cost,
            'costs': {
                "walk": values[4],
                "car": values[5],
                "BRP": values[6],
                "4x4": values[7]
            }
        })
        #print('arriva2')
        startkey=self.getKey(start)
        while key != startkey:
            #print(startkey)
            #print(key)
            predecesor = self.myrouter.findPredecesor(key, vehicle)
            values = self.myrouter.findPredecesorValues(key, vehicle)
            #print(str(j))
            #-148968,-148940
            key, j, vehicle = predecesor[0], predecesor[1], predecesor[2]
            rampPos, rampNeg, dist, cost = values[0],values[1],values[2],values[3]
            route.append({
                'coordinates':[float(self.nodes[key]['coor'][0]),float(self.nodes[key]['coor'][1])],
                'point':key,
                'vehicle':vehiclesSTR[vehicle],
                'posRamp':rampPos,
                'negRamp':rampNeg,
                'dist':dist,
                'cost':cost,
                'costs': {
                    "walk": values[4],
                    "car": values[5],
                    "BRP": values[6],
                    "4x4": values[7]
                }
            })
            #print(route)
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




