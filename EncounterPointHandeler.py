import psycopg2
import xml.etree.ElementTree as ET
import json

with open('configurationFiles/database.json') as json_file:
    configuration_data = json.load(json_file)

def retriveEncounterPoints():
    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])

    cursorEnconterPoints = conn.cursor()

    cursorEnconterPoints.execute("SELECT name, ST_AsKML(geom)"
        " FROM public.\"COE_montserrat_punts\""
        " where folderpath like '%Punt de trobada%' ;");
    pointsList = cursorEnconterPoints.fetchall()
    points=[]
    for name, point in pointsList:
        root = ET.fromstring(point)
        for child in root:
            data=child.text.split(',')
            obj={
                'coordinates': [float(data[1]),float(data[0])],
                'name': name,
                'type': -1
            }
            points.append(obj)
        #print(root.Point.coordinates)
    conn.close()

    return points

def isPredecesorListEmpty():
    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])

    cursorEnconterPoints = conn.cursor()
    cursorEnconterPoints.execute("Select count(*) from predecesorList;")
    value=cursorEnconterPoints.fetchone()
    print(value[0])
    return value[0]==0

def insertPredecesorList(predecesors,final):

    conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                            password=configuration_data["password"], host=configuration_data["host"])
    query="Insert into predecesorList values "
    first=True
    for el in predecesors:
        if(not first):
            query +=","
        first=False
        query+="("+str(final)+"," \
                + str(el["from"])+"," \
                + str(el["to"])+"," \
                + str(el["vehicle"])+"," \
                + str(el["posRamp"])+"," \
                + str(el["negRamp"])+"," \
                + str(el["dist"])+"," \
                + str(el["cost"])+"," \
                + str(el["costu"]["walk"])+"," \
                + str(el["costu"]["car"])+"," \
                + str(el["costu"]["BRP"])+"," \
                + str(el["costu"]["4x4"])+")"
    query +=";"

    cursorEnconterPoints = conn.cursor()
    cursorEnconterPoints.execute(query)
    conn.commit()


#print(len(retriveEncounterPoints()))