import time

import psycopg2
import json

maxDist=1

with open('configurationFiles/database.json') as json_file:
    configuration_data = json.load(json_file)

def nearestFinalNode(lat,lon):
    initTime=time.time()
    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])

    cursorpointsToGet = conn.cursor()
    setupTime=time.time()#+str(lon)+","+str(lat)+
    cursorpointsToGet.execute("SELECT fi.id, ST_Distance("
		"ST_SetSRID(ST_MakePoint( "+str(lon)+","+str(lat)+ " ),4326)," 
		" fi.geom) AS dist"
	" FROM final_nodes fi"
    "where fi.geom && ST_Expand(ST_SetSRID(ST_MakePoint( "+str(lon)+","+str(lat)+ " ),4326), 2000)"
	" order by dist ASC"
        " LIMIT 1;");
    print('query')
    print(time.time()-setupTime)
    print('setup')
    print(setupTime-initTime);
    point = cursorpointsToGet.fetchone()
    if(point[1]<maxDist):
        return point[0]
    print('faar')
    print(point[1])
    return None


def nearestFinalNodes(nodes):
    ends=[]
    initTime=time.time()
    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])
    for final in nodes:
        cursorpointsToGet = conn.cursor()
        setupTime = time.time()
        '''
        cursorpointsToGet.execute("SELECT fi.id, ST_Distance("
                " ST_SetSRID(ST_MakePoint("+str(final['coordinates'][1])+","+str(final['coordinates'][0])+"),4326)," 
                " fi.geom) as dist"
            " FROM final_nodes fi"
            " WHERE fi.geom && ST_Expand(ST_SetSRID(ST_MakePoint("+str(final['coordinates'][1])+","+str(final['coordinates'][0])+"),4326), 200)"
            " order by dist ASC"
            " limit 1;")
        '''
        cursorpointsToGet.execute("SELECT fi.id, ST_Distance("
                " ST_SetSRID(ST_MakePoint(" + str(final['coordinates'][1]) + "," +
                                  str(final['coordinates'][0]) + "),4326),"
            " fi.geom) as dist"
            " FROM final_nodes fi"
            " order by fi.geom <->ST_SetSRID(ST_MakePoint(" + str(final['coordinates'][1]) + "," +
                                  str(final['coordinates'][0]) + "),4326)"
            " Limit 1;")
        print('query')
        print(time.time() - setupTime)
        point = cursorpointsToGet.fetchone()
        if (point[1] < maxDist):
            final['point'] = point[0]
            ends.append(final)
    print('all time')
    print(time.time() - setupTime)
    conn.close()
    return ends


def nearestFinalNodes2(nodes):
    ends=[]
    initTime=time.time()
    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])
    cursorpointsToGet = conn.cursor()
    cursorpointsToGet.execute("Delete from temp_vehiclePositions;")
    i=0;
    finalList=[]
    for final in nodes:
        cursorpointsToGet.execute("Insert into temp_vehiclePositions values("+str(i)+","
                    "ST_SetSRID(ST_MakePoint("+str(final['coordinates'][1])+","+str(final['coordinates'][0])+"),4326));")
        i+=1
        finalList.append(final)
    conn.commit()
    print('commit done')
    '''
    cursorpointsToGet.execute("SELECT fi.id, ve.id_v, ST_Distance(fi.geom,ve.geom)"
        " FROM final_nodes fi, temp_vehiclePositions ve"
        " ORDER BY fi.geom <-> ve.geom"
        " LIMIT 1")
        
    cursorpointsToGet.execute("SELECT fi.id, b.id_v, ST_Distance(b.geom, fi.geom)"
    " FROM graph_nodes_geometry fi"
    " JOIN LATERAL( SELECT ve.id_v as id_v, ve.geom as geom"
    " FROM temp_vehiclePositions ve"
    " ORDER BY ve.geom <-> fi.geom"
    " LIMIT 1) AS b"
    " ON true;")
    '''
    cursorpointsToGet.execute("SELECT b.id, ve.id_v, ST_Distance(b.geom, ve.geom)"
    " FROM temp_vehiclePositions ve"
    " JOIN LATERAL( SELECT fi.id as id, fi.geom as geom"
    " FROM graph_nodes_geometry fi"
    " ORDER BY ve.geom <-> fi.geom"
    " LIMIT 1) AS b"
    " ON true;")
    points = cursorpointsToGet.fetchall()
    minDistC=maxDist
    maxDistC=0
    for pointId, fi, dist in points:
        if(dist>maxDistC):
            maxDistC=dist
        if(dist<minDistC):
            minDistC=dist
        if (dist < maxDist):
            if(pointId==246488):
                print("found")
            finalList[fi]['point'] = pointId
            ends.append(finalList[fi])
        else:
            print(dist)
    print("maxDistC")
    print(maxDistC)
    print("minDistC")
    print(minDistC)
    print(len(ends))
    conn.close()
    return ends