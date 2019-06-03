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

#print(len(retriveEncounterPoints()))