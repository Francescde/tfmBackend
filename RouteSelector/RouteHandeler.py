from RouteSelector.VehiclesHandeler import vehicles
from RouteSelector.MapHandeler import MapHandeler
from RouteSelector.originHandeler import give_origins, giveVehiclesStr
from RouteSelector.EncounterPointHandeler import retriveEncounterPoints
from RouteSelector.pointHandeler import nearestFinalNodes2, removeUnexploredNodes, nearestFinalNodes3, \
    getCOENearestNode, removeUnexploredNodes2
import time

def min_route_walking(routes):
    minWalking=999999
    routeS=[]
    pos=0
    cost0=999999
    for key, route in routes.items():
        i=0
        #print(route[i])
        while(i<len(route) and route[i]['vehicle']!='walk'):
            i=i+1
        if(i<len(route)):
            if route[i]['cost']<=minWalking:
                if route[i]['cost']==minWalking:
                    if(cost0>route[0]['cost']):
                        minWalking=route[i]['cost']
                        routeS=route
                        pos=i
                        cost0 = route[0]['cost']
                else:
                    minWalking=route[i]['cost']
                    routeS=route
                    pos=i
                    cost0 = route[0]['cost']
        else:
            if route[i-1]['cost']<=minWalking:
                if route[i-1]['cost']==minWalking:
                    if(cost0>route[0]['cost']):
                        minWalking=route[i-1]['cost']
                        routeS=route
                        pos=i-1
                        cost0 = route[0]['cost']
                else:
                    minWalking=route[i-1]['cost']
                    routeS=route
                    pos=i-1
                    cost0 = route[0]['cost']
    return routeS, pos, minWalking, routeS[0]['point']

def minWalkingData(route):
    i=len(route)-1
    while (i >0 and route[i]['vehicle'] == 'walk'):
        i = i - 1
    pos = i
    return pos, route[0]['point']

def min_route(routes):
    routeS=[]
    cost0=9999999
    for key, route in routes.items():
        if (cost0 > route[0]['cost']):
            routeS = route
            cost0 = route[0]['cost']
    i=len(routeS)-1
    while(i>0 and routeS[i]['vehicle']=='walk'):
        i=i-1
    pos=i
    minWalking = routeS[pos]['cost']
    return routeS, pos, minWalking, routeS[0]['point']

class RouteHandeler():

    def __init__(self,vehiclesFile=None):
        global ends
        global encPoints
        mapHandeler=MapHandeler()
        self.graphMultimodal, self.graphUnimodal = mapHandeler.read_graph("maps/mapFusionJoinedGRAPH.osm",187767,vehicles)

        #agafa punts de trobada i crea llista fins a ells
        encPoints = retriveEncounterPoints()
        encPoints = nearestFinalNodes2(encPoints)
        # borra totes les llistes de precedencies de bd
        #for enc in encPoints:
        enc=encPoints[0]
        timeTostorePredecesors = time.time()
        # obte la llista de precedencies
        unexploredList = self.graphUnimodal.getUnexplored(enc['point'])
        removeUnexploredNodes2(unexploredList)
        # guardala a bd
        # insertPredecesorList(predecesorList,enc['point'])
        print(time.time() - timeTostorePredecesors, "time to store predecesors")
        print(len(unexploredList))
        # Per cada LLista s'incerta
        # print(predecesorList)



        timeToreadPoints=time.time()
        encPoints = retriveEncounterPoints()
        #nodes en el graf de vehicles
        encPoints = nearestFinalNodes2(encPoints)
        #nodes en el graf multimodal
        for end in encPoints:
            end['encounter']=self.graphMultimodal.getNearestNode(end["coordinates"][0],end["coordinates"][1])
        print("time to read encounter points")
        print(time.time() - timeToreadPoints)
        '''
        timeToreadPoints=time.time()
        if(isPredecesorListEmpty()):
            encPoints = retriveEncounterPoints()
            encPoints=nearestFinalNodes2(encPoints)
            #borra totes les llistes de precedencies de bd
            for enc in encPoints:
                timeTostorePredecesors=time.time()
                predecesorList={}
                for vehicle in [0,1,2,3]:
                    self.graphUnimodal.solve(enc['point'], vehicle)
                    #obte la llista de precedencies
                    predecesorList[vehicle]=self.graphUnimodal.getAllPredecesors(vehicle,enc['point'])
                    #guardala a bd
                #insertPredecesorList(predecesorList,enc['point'])
                print(time.time()-timeTostorePredecesors,"time to store predecesors")
                print(len(predecesorList))
                #Per cada LLista s'incerta
                #print(predecesorList)
        print("time to read encounter points")
        print(time.time() - timeToreadPoints)
        '''
        if(vehiclesFile!=None):
            self.addEndsFromFile(vehiclesFile)

    def addEndsFromFile(self,file):
        global ends
        timeToreadPoints=time.time()
        finals = give_origins(file)
        ends=nearestFinalNodes3(finals)
        for final in ends:
            self.graphUnimodal.addfinal(final['point'])
        print(len(ends))
        print("time to read points")
        print(time.time()-timeToreadPoints)


    def getRoutes(self,lat,lon):
        global ends
        start = self.graphMultimodal.getNearestNode(lat, lon)
        #-123204
        #41.7410791,1.849642 Manresa
        #41.568004,2.0237163
        #41.5891303,1.6078417
        #
        #ends = [-131168, -102262, -124744, -157746]#[-143102, -170904, -107948, -81882, -44288, -50156,-123204]
        self.graphMultimodal.solve(start, ends)
        routes = {}
        for end in ends:
            routes[str(end['name']) + "To_Position"] = self.graphMultimodal.getRoute(end['point'], start, 1)
        return routes

    def findMaxPosForVehicle(self,route,pos,vehicle):
        i=pos
        #print('route')
        if(i==len(route)-1):
            i=i-1
        #print(route[i]['point'])
        while(i>0 and not self.graphMultimodal.findVehicleCanGoToPred(route[i]['point'],vehicle)):
            i=i-1
            #print(route[i]['point'])
        if(i<pos):
            i=i+1
        if(i>=len(route)):
            i=len(route)-1
        #print('route done')
        return i

    def getRoutesWithMandatory(self,lat,lon,vehicles):
        global ends
        global encPoints
        maxPoints=3
        start, extraPoint, dist_from_start, dist_to_point = getCOENearestNode(lat, lon)
        #start = self.graphMultimodal.getNearestNode(lat, lon)
        #-123204
        #[-131168, -102262, -124744, -157746]#[-143102, -170904, -107948, -81882, -44288, -50156,-123204]
        endsPointList=[end['encounter'] for end in encPoints]
        timeStartMultimodal=time.time()
        timegloablalMultimodal=time.time()
        self.graphMultimodal.solve(start, endsPointList)
        print('solve multimodal')
        print(time.time()-timeStartMultimodal)
        timeExplore=time.time()-timeStartMultimodal
        vehiclesSTR=giveVehiclesStr()
        routes = {}
        meetingPoints={}
        routeSel={}
        timePoints=0
        timeGetRoutes=0
        #for end in ends:
        encPointsToExplore=[]
        for end in encPoints:
            pred=self.graphMultimodal.findPredecesor(self.graphMultimodal.nodesInv[end['encounter']], 1)
            if (pred[0] >= 0 and end != start):
                values = self.graphMultimodal.myrouter.findPredecesorValues(self.graphMultimodal.nodesInv[end['encounter']], 1)
                end["value"]=values[3]
                encPointsToExplore.append(end)
            if(end==start):
                encPointsToExplore=[end]
                break
        encPointsToExplore = sorted(encPointsToExplore, key=lambda k: k['value'])
        #print(encPointsToExplore)
        #print('-----------------------------------------------------------------')
        encPointsToExplore=[encPointsToExplore[i] for i in range(0,min(maxPoints,len(encPointsToExplore)))]
        encPointsDic={}
        for end in encPointsToExplore:
            timeStartGetRoutes=time.time()
            routeSolved, maxCar, maxBRP, max4x4 =self.graphMultimodal.getRoute(end['encounter'], start)
            if(len(routeSolved)>0):
                encPointsDic[str(end['name'])]=end
                route_name=str(end['name'])
                routes[route_name] = routeSolved
                ''''''
                timeGetRoutes = timeGetRoutes + (time.time() - timeStartGetRoutes)
                timeStarPoints = time.time()
                vahiclesPos = [maxCar, maxBRP, max4x4]
                pos = max(vahiclesPos)
                sel = {
                    'points': routeSolved,
                    'routeName': route_name,
                    'changePoint': pos,
                    'subrutes': {}
                }
                routeSel[route_name] = sel
                if pos >= 0:
                    # print(route_name)
                    for vehicle in vehicles:
                        if (end['type'] == -1 or end['type'] == vehicle):
                            pos2 = vahiclesPos[vehicle - 1]
                            routeSolved[pos2]['limitVehicle'] = vehiclesSTR[vehicle]
                            if (end['name'] not in meetingPoints.keys()):
                                obj = {
                                    'route': route_name,
                                    'vehicle': vehicle
                                }
                                meetingPoints[end['name']] = {}
                                meetingPoints[end['name']]['points'] = [obj]
                                meetingPoints[end['name']]['vehicles'] = [vehicle]
                            else:
                                obj = {
                                    'route': route_name,
                                    'vehicle': vehicle
                                }
                                meetingPoints[end['name']]['points'].append(obj)
                                if vehicle not in meetingPoints[end['name']]['vehicles']:
                                    meetingPoints[end['name']]['vehicles'].append(vehicle)
                timePoints = timePoints + (time.time() - timeStarPoints)
                '''
            else
                newpoint=self.graphMultimodal.getNearestNodeSolved(end['coordinates'][0], end['coordinates'][1])
                if(newpoint is not None):
                    end['point'] = newpoint
                    routeSolved, maxCar, maxBRP, max4x4 = self.graphMultimodal.getRoute(end['point'], start)
                    if (len(routeSolved) > 0):
                        route_name=str(end['name'])
                        routes[route_name] = routeSolved
                else:
                    unsolvingEnds.append(end)
                    solved=False
            timeGetRoutes=timeGetRoutes+(time.time()-timeStartGetRoutes)
            timeStarPoints=time.time()
            if solved:
                vahiclesPos=[maxCar, maxBRP, max4x4]
                pos=max(vahiclesPos)
                sel={
                    'points':routeSolved,
                    'routeName':route_name,
                    'changePoint': pos,
                    'subrutes':{}
                }
                routeSel[route_name] = sel
                if pos>0:
                    #print(route_name)
                    for vehicle in vehicles:
                        if(end['type']==-1 or end['type']==vehicle):
                            pos2 = vahiclesPos[vehicle-1]
                            routeSolved[pos2]['limitVehicle']=vehiclesSTR[vehicle]
                            if (routeSolved[pos]['point'] not in meetingPoints.keys()):
                                obj={
                                    'route':route_name,
                                    'vehicle':vehicle
                                }
                                meetingPoints[routeSolved[pos]['point']]={}
                                meetingPoints[routeSolved[pos]['point']]['points']=[obj]
                                meetingPoints[routeSolved[pos]['point']]['vehicles']=[vehicle]
                            else:
                                obj={
                                    'route':route_name,
                                    'vehicle':vehicle
                                }
                                meetingPoints[routeSolved[pos]['point']]['points'].append(obj)
                                if vehicle not in meetingPoints[routeSolved[pos]['point']]['vehicles']:
                                    meetingPoints[routeSolved[pos]['point']]['vehicles'].append(vehicle)
            i=1
            timePoints=timePoints+(time.time()-timeStarPoints)
        ends = [elemnt for elemnt in ends if elemnt not in unsolvingEnds]
        '''
        print('time multimodal')
        print(time.time()-timegloablalMultimodal)
        print(timeGetRoutes)
        print(timePoints)

        timegloablaUnimodals=time.time()
        selSubrutes={}
        meetingPoints2={}
        #print(meetingPoints.keys())
        #print('------------------------------')
        for meetPoint in meetingPoints.keys():
            subroutes={}
            meetPoint2={
                'vehicles':meetingPoints[meetPoint]['vehicles'],
                'points':[]
            }
            for vehicle in meetingPoints[meetPoint]['vehicles']:
                #print(meetingPoints[meetPoint]['vehicles'])
                #print(encPointsDic[meetPoint])
                timeToExplore=time.time()
                self.graphUnimodal.solve(encPointsDic[meetPoint]['point'], vehicle)
                timeExplore += time.time() - timeToExplore
                #print('solved')
                for end in ends:
                    if(end['type']==-1 or end['type']==vehicle):
                        obj = {
                            'route': str(end['name']),
                            'vehicle': vehicle
                        }
                        meetPoint2['points'].append(obj)
                        sub_route_name=str(end['name'])+'_'+vehiclesSTR[vehicle]
                        #print(end['point'])
                        subroute = self.graphUnimodal.getRoute(end['point'],encPointsDic[meetPoint]['point'],vehicle)
                        #print('solved',len(subroute))
                        if(len(subroute)>0):
                            R2dist = subroute[0]['cost']
                            route2dist = R2dist
                            ##print(routes2)
                            sel = {
                                'points': subroute,
                                'changePoint': pos2,
                                'routeName': route_name,
                            }
                            subroutes[sub_route_name] = sel
            selSubrutes[meetPoint]=subroutes
            meetingPoints2[meetPoint]=meetPoint2
            '''
            for point in meetingPoints[meetPoint]['points']:
                for subroute in subroutes.keys():
                    routeSel[point['route']]['subrutes'][subroute]=subroutes[subroute]
                    '''


        print('totaltime')
        print(time.time()-timegloablalMultimodal)
        print(timeExplore)


        #print(encPoints)
        #print(routeSel)
        return {
            'meetPoints': meetingPoints2,
            'subroutes': selSubrutes,
            'multimodal': routeSel
        }
        #return routeSel

