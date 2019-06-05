import psycopg2
import time
from RouteSelector.router.routerTotal import routerc
from RouteSelector.router.routerSingle import routerc as routercS
import json

with open('configurationFiles/database.json') as json_file:
    configuration_data = json.load(json_file)


INF=9999

numNodes = 468496
div = 10000000
INF=9999

def walkingCost( distance, positiveRmp, negativeRmp, type, footSpeeds):
    if (type['type'] == "track"):
        tracktype = type["tracktype"]
        speed = str(footSpeeds[type['type']][tracktype])
    else:
        speed = str(footSpeeds[type['type']])
    if speed =='inf':
        return INF
    speed=float(speed)/3.6
    cost = distance / speed
    inclinationpos = positiveRmp / distance
    inclinationneg = -negativeRmp / distance
    cost = cost * (1 + inclinationpos) * (1 + (inclinationneg / 3))
    return cost


def vehicleCost( distance, type, oneway, vehicle):
    if oneway:
        cost = INF
    else:
        if (type['type'] == "track"):
            tracktype = type["tracktype"]
            speed = str(vehicle[type['type']][tracktype])
        else:
            speed = str(vehicle[type['type']])
        if speed =='inf':
            return INF
        speed=float(speed)/3.6
        cost = distance / speed
    return cost

class MapHandeler():

    def read_graph(self,filename,numNodes,vehicles):
        numNodes = 468496
        conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                                password=configuration_data["password"], host=configuration_data["host"])

        cursorWaysToSet = conn.cursor()
        cursorNodesToSet = conn.cursor()

        graph = routerc(numNodes)
        graph2 = routercS(numNodes)


        ini = 0
        numWay = 0

        cursorNodesToSet.execute("select osmn.id, osmn.lat, osmn.lon"
                                 " FROM public.planet_osm_nodes osmn"
                                 " where osmn.id in (select wp.id_node from public.way_point wp where wp.is_limit is TRUE);");
        points = cursorNodesToSet.fetchall()
        numPunts = 0
        for id_node, latI, lonI in points:
            lat = latI / div
            lon = lonI / div
            graph2.addNode(id_node, str(lat), str(lon))
            if (numPunts - ini == 10000):
                print('num points')
                print(numPunts)
                ini = numPunts
            numPunts += 1

        ini = 0
        print("punts fets")
        cursorWaysToSet.execute("SELECT wr.id_way,"
	        " array(select wp.id_node from public.way_point wp"
	            " where wp.id_way=wr.id_self_key and  wp.is_limit is TRUE"
	            " Order By wp.way_position) as points,"
	        " wr.dist, wr.ramp_neg, wr.ramp_pos, wr.oneway, wr.highway_type"
            " FROM public.way_relation wr "
            " where wr.dist>0;");
        print("comença ways")
        ways = cursorWaysToSet.fetchall()
        timer=time.time()
        timerCalculAdd=0
        timeToGrafAdd=0
        for id_way, pointsList, distDec, ramp_negDec, ramp_posDec, oneway, highway_type in ways:
            if (len(pointsList)>2):
                print("erooooooor")
                break
            dist = float(distDec)
            ramp_neg = float(ramp_negDec)
            ramp_pos = float(ramp_posDec)

            highway = {
                'type': highway_type,
                "tracktype": "grade1"
            }

            timerCalcul=time.time()
            walkingCost1 = walkingCost(dist, ramp_pos, ramp_neg, highway, vehicles['Foot'])
            CarCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['Car'])
            BRPCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['BRP'])
            AllTerrainCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['4x4'])
            # print(str(pointsList) + " " + str(walkingCost1) + " " + str(CarCost1) + " " + str(BRPCost1) + " " + str(AllTerrainCost1))
            graph2.inicializeEdge(pointsList[1], pointsList[0], walkingCost1, CarCost1, BRPCost1,
                                 AllTerrainCost1, ramp_pos,
                                 ramp_neg, dist)
            # print('next')

            walkingCost2 = walkingCost(dist, ramp_neg * -1, ramp_pos * -1, highway, vehicles['Foot'])
            CarCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['Car'])
            BRPCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['BRP'])
            AllTerrainCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['4x4'])

            timerCalculAdd += time.time()-timerCalcul;
            timeToGraf=time.time()
            # print(str(pointsList[1]) + " " + str(pointsList[0]) + " " + str(walkingCost2) + " " + str(CarCost2) + " " + str(BRPCost2) + " " + str(AllTerrainCost2))
            graph2.inicializeEdge(pointsList[0], pointsList[1], walkingCost2, CarCost2, BRPCost2,
                                 AllTerrainCost2, ramp_neg * -1,
                                 ramp_pos * -1, dist)
            timeToGrafAdd+=time.time()-timeToGraf
            # print('numway')
            # print(numWay)
            if (numWay - ini == 10000):
                print('numway')
                print(numWay)
                ini = numWay
            numWay += 1
        ###########################################################
        ini = 0
        numWay = 0

        cursorNodesToSet.execute("select osmn.id, osmn.lat, osmn.lon"
                                 " FROM public.coe_nodes osmn"
                                 " where osmn.id in (select wp.id_node from public.coe_way_point wp where wp.is_limit is TRUE);");
        points = cursorNodesToSet.fetchall()
        numPunts = 0
        for id_node, latI, lonI in points:
            lat = latI / div
            lon = lonI / div
            graph.addNode(id_node, str(lat), str(lon))
            if (numPunts - ini == 10000):
                print('num points')
                print(numPunts)
                ini = numPunts
            numPunts += 1

        ini = 0
        print("punts fets")
        cursorWaysToSet.execute("SELECT wr.id_way,"
                                " array(select wp.id_node from public.coe_way_point wp"
                                " where wp.id_way=wr.id_self_key and  wp.is_limit is TRUE"
                                " Order By wp.way_position) as points,"
                                " wr.dist, wr.ramp_neg, wr.ramp_pos, wr.oneway, wr.highway_type"
                                " FROM public.coe_way_relation wr "
                                " where wr.dist>0;");
        print("comença ways")
        ways = cursorWaysToSet.fetchall()

        for id_way, pointsList, distDec, ramp_negDec, ramp_posDec, oneway, highway_type in ways:
            if (len(pointsList) > 2):
                print("erooooooor")
                break
            dist = float(distDec)
            ramp_neg = float(ramp_negDec)
            ramp_pos = float(ramp_posDec)

            highway = {
                'type': highway_type,
                "tracktype": "grade1"
            }

            timerCalcul = time.time()
            walkingCost1 = walkingCost(dist, ramp_pos, ramp_neg, highway, vehicles['Foot'])
            CarCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['Car'])
            BRPCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['BRP'])
            AllTerrainCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['4x4'])
            # print(str(pointsList) + " " + str(walkingCost1) + " " + str(CarCost1) + " " + str(BRPCost1) + " " + str(AllTerrainCost1))

            # print('next')
            graph.inicializeEdge(pointsList[1], pointsList[0], walkingCost1, CarCost1, BRPCost1,
                                  AllTerrainCost1, ramp_pos,
                                  ramp_neg, dist)

            walkingCost2 = walkingCost(dist, ramp_neg * -1, ramp_pos * -1, highway, vehicles['Foot'])
            CarCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['Car'])
            BRPCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['BRP'])
            AllTerrainCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['4x4'])

            timerCalculAdd += time.time() - timerCalcul;
            timeToGraf = time.time()
            # print(str(pointsList[1]) + " " + str(pointsList[0]) + " " + str(walkingCost2) + " " + str(CarCost2) + " " + str(BRPCost2) + " " + str(AllTerrainCost2))

            graph.inicializeEdge(pointsList[0], pointsList[1], walkingCost2, CarCost2, BRPCost2,
                                  AllTerrainCost2, ramp_neg * -1,
                                  ramp_pos * -1, dist)
            timeToGrafAdd += time.time() - timeToGraf
            # print('numway')
            # print(numWay)
            if (numWay - ini == 10000):
                print('numway')
                print(numWay)
                ini = numWay
            numWay += 1
        ##############




        print('numway')
        print(numWay)
        print()
        print('temps')
        porta=time.time()-timer
        print(porta)
        print(timerCalculAdd)
        print('% de temps de no calcul')
        print((porta-timerCalculAdd)/porta)
        print('% de temps de calcul')
        print((timerCalculAdd)/porta)
        print('% de temps de add')
        print((timeToGrafAdd)/porta)
        print()
        #DataFile = open("pointData.json", "w")
        #DataFile.write(simplejson.dumps(graph.returnNodes(), indent=4, sort_keys=True))
        #DataFile.close()
        return graph, graph2
