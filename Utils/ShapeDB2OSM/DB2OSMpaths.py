import psycopg2
import utm
import re
import xml.etree.ElementTree as ET

conn=psycopg2.connect(database="Montserrat2", user="postgres", password="Montserrat", host="localhost")

global id_points
global points_lat_lon_z

id_points=-1
points_lat_lon_z=[]

def read_points_from_path(paths,file,i):
        global id_points
        global points_lat_lon_z
        cursor=conn.cursor()
        path={}
        command="SELECT ST_AsText(geom) FROM public.\""+str(file)+"\" WHERE id="+str(i)+";"
        cursor.execute(command)
        n=str(cursor.fetchall())
        ##llegir primer punt, guardar a taula points, incrementar id_points, asociar id_points amb path primer punt

        #print(n)
        pos = re.search("\d", n)
        n = n[pos.start():]
        n = n[::-1]
        pos = re.search("\d", n)
        n = n[pos.start():]
        n = n[::-1]

        lines = n.split('),')
        paths_in_multiline = []
        for line in lines:
                line = line.replace('(', '')
                paths_in_multiline.append(line)
        for line in paths_in_multiline:
                points_path = []
                points = line.split(',')
                for point in points:
                        #print('point')
                        lat_lon_z = point.split(' ')
                        lat, lon = utm.to_latlon(float(lat_lon_z[0]),float(lat_lon_z[1]),31,'U')
                        points_path.append([lon,lat])
                        if not (lat_lon_z in points_lat_lon_z):
                               points_lat_lon_z.append([lon,lat])
                command="SELECT name, folderpath FROM public.\""+str(file)+"\" WHERE id="+str(i)+";"
                cursor.execute(command)
                n=cursor.fetchone()
                name=n[0]
                folder=n[1]
                path={}
                path["name"]=name
                path["folder"]=folder
                path["points"]=points_path
                paths.append(path)


def read_paths(lines2,doc,file,c,category,tag):
        paths=[]
        path={}
        points={}
        cursor=conn.cursor()
        i=1
        c=3
        n=3
        while(str(n)!= "None"):
                cursor=conn.cursor()
                command="SELECT name FROM public.\""+str(file)+"\" WHERE id="+str(i)+";"
                cursor.execute(command)
                n=cursor.fetchone()
                if(str(n)!="None"):
                        command="SELECT name FROM public.\""+str(file)+"\" WHERE id="+str(i)+";"
                        cursor.execute(command)
                        n=cursor.fetchone()
                        path["name"]=n
                        read_points_from_path(paths,file,i)
                        i+=1
                conn.commit()
                cursor.close()
        for i in range(0,len(points_lat_lon_z)):
                doc.write("  <node id='"+str(-i-1)+"' action='modify' lat='"+str(points_lat_lon_z[i][1])+"' lon='"+str(points_lat_lon_z[i][0])+"' />\n")
                id_points=-i-1
                c+=1
        id_points -= 1
        cursorEnconterPoints = conn.cursor()

        cursorEnconterPoints.execute("SELECT name, ST_AsKML(geom)"
                                     " FROM public.\"COE_montserrat_punts\""
                                     " where folderpath like '%Punt de trobada%' ;");
        pointsList = cursorEnconterPoints.fetchall()
        for name, point in pointsList:
                root = ET.fromstring(point)
                for child in root:
                        data = child.text.split(',')
                        lat, lon = float(data[1]), float(data[0])
                        doc.write("  <node id='"+str(id_points)+"' action='modify' lat='"+str(lat)+"' lon='"+str(lon)+"'>\n"
                                                "    <tag k='name' v='"+name+"' />\n"
                                        "  </node>\n")
                        id_points -= 1
        for i in range(0,len(paths)):
                        doc.write(" <way id='"+str(id_points-i)+"' action='modify'>\n")
                        c+=1
                        for x in range(0,len(paths[i]["points"])):
                                n=points_lat_lon_z.index(paths[i]["points"][x])
                                doc.write("  <nd ref='"+str(-n-1)+"' />\n")
                                c+=1
                        if(paths[i]["name"]!="NULL"):
                                doc.write("  <tag k='name' v='"+paths[i]["name"].replace("'", "&apos;")+"' />\n")
                                c+=1
                        if(paths[i]["folder"]!="NULL"):
                                doc.write("  <tag k='folder' v='"+paths[i]["folder"].replace("'", "&apos;")+"' />\n")
                                c+=1
                        doc.write("  <tag k='ogc_fid' v='"+str(i + 1)+"' />\n")
                        doc.write("  <tag k='"+category+"' v='"+tag+"' />\n")
                        doc.write(" </way>\n")
                        c+=3
        doc.write("</osm>\n")

def read_table_from_db(file,category,tag):
        i=0
        lines = []
        doc = open(file+".osm", "w")
        doc.write("<?xml version='1.0' encoding='UTF-8'?>")
        doc.write("<osm version='0.6' generator='Python Script'>")
        read_paths(lines,doc,file,2,category,tag)
        doc.close()

def main():
        read_table_from_db('COE_montserrat_linies','highway','path')

main()
