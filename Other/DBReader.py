import time

import psycopg2
from RouteSelector.VehiclesHandeler import vehicles
from RouteSelector.router.routerTotal import routerc
from RouteSelector.router.routerSingle import routerc as routercS
import json

with open('configurationFiles/database.json') as json_file:
    configuration_data = json.load(json_file)

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

readerTime=time.time()



conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                        password=configuration_data["password"], host=configuration_data["host"])

cursorWaysToSet = conn.cursor()
cursorNodesToSet = conn.cursor()
ini=0


graph=routerc(numNodes)
graph2=routercS(numNodes)
numWay = 0

cursorNodesToSet.execute("select osmn.id, osmn.lat, osmn.lon"
    " FROM public.planet_osm_nodes osmn"
    " where osmn.id in (select wp.id_node from public.way_point wp where wp.is_limit is TRUE);");
points = cursorNodesToSet.fetchall()
numPunts=0
for id_node, latI, lonI in points:
    lat= latI/div
    lon= lonI/div
    graph.addNode(id_node,str(lat),str(lon))
    graph2.addNode(id_node,str(lat),str(lon))
    if(numPunts-ini==10000):
        print('num points')
        print(numPunts)
        ini=numPunts
    numPunts+=1

ini=0
print("punts fets")
cursorWaysToSet.execute("SELECT wp.id_way, wp.id_node, wr.dist, wr.ramp_neg, wr.ramp_pos, wr.oneway, wr.highway_type"
    " FROM public.way_point wp, public.way_relation wr"
    " where wp.id_way=wr.id_self_key and  wp.is_limit is TRUE"
    " Order By wp.id_way, wp.way_position;");
print("comença ways")
ways = cursorWaysToSet.fetchall()
pointsList=[]
idWayList=[]
for id_way, id_node, distDec, ramp_negDec, ramp_posDec, oneway, highway_type in ways:
    dist=float(distDec)
    ramp_neg=float(ramp_negDec)
    ramp_pos=float(ramp_posDec)

    highway={
        'type':highway_type,
        "tracktype": "grade1"
    }

    pointsList.append(id_node)
    idWayList.append(id_way)
    if(len(pointsList)==2):

        if dist > 0:
            walkingCost1 = walkingCost(dist, ramp_pos, ramp_neg, highway, vehicles['Foot'])
            CarCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['Car'])
            BRPCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['BRP'])
            AllTerrainCost1 = vehicleCost(dist, highway, oneway == -1, vehicles['4x4'])
            #print(str(pointsList) + " " + str(walkingCost1) + " " + str(CarCost1) + " " + str(BRPCost1) + " " + str(AllTerrainCost1))
            graph.inicializeEdge(pointsList[1], pointsList[0], walkingCost1, CarCost1, BRPCost1, AllTerrainCost1, ramp_pos,
                                 ramp_neg, dist)
            #print('next')
            graph2.inicializeEdge(pointsList[1], pointsList[0], walkingCost1, CarCost1, BRPCost1, AllTerrainCost1, ramp_pos,
                                  ramp_neg, dist)
        if dist > 0:
            walkingCost2 = walkingCost(dist, ramp_neg * -1, ramp_pos * -1, highway, vehicles['Foot'])
            CarCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['Car'])
            BRPCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['BRP'])
            AllTerrainCost2 = vehicleCost(dist, highway, oneway == 1, vehicles['4x4'])
            #print(str(pointsList[1]) + " " + str(pointsList[0]) + " " + str(walkingCost2) + " " + str(CarCost2) + " " + str(BRPCost2) + " " + str(AllTerrainCost2))
            graph.inicializeEdge(pointsList[0], pointsList[1], walkingCost2, CarCost2, BRPCost2, AllTerrainCost2, ramp_neg * -1,
                                 ramp_pos * -1, dist)
            graph2.inicializeEdge(pointsList[0], pointsList[1], walkingCost2, CarCost2, BRPCost2, AllTerrainCost2, ramp_neg * -1,
                                  ramp_pos * -1, dist)
        if(idWayList[0]!=idWayList[1]):
            print("erooooooor")
            break
        #print('numway')
        #print(numWay)
        if(numWay-ini==10000):
            print('numway')
            print(numWay)
            ini=numWay
        numWay+=1
        pointsList=[]
        idWayList=[]

print("done")
conn.close()

print('reader Time')
print(time.time() - readerTime)
