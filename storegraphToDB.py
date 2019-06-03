import math

import gdal
import osr
# from osgeo import gdal
# from osgeo import osr
import psycopg2
import json

with open('configurationFiles/database.json') as json_file:
    configuration_data = json.load(json_file)


higwaytags=["path","motorway","trunk","primary","secondary","tertiary","unclassified","residential","motorway_link",
      "trunk_link","primary_link","secondary_link","tertiary_link","living_street","service","pedestrian","track",
      "road","footway","steps","path"]
onewaySTR="oneway"
onewayDirTags = {
    "yes": 1,
    "no": 0,
    "-1": -1
}

gdal.AllRegister()  # register all drivers
gdal.UseExceptions()

'''http://monkut.webfactional.com/blog/archive/2012/5/2/understanding-raster-basic-gis-concepts-and-the-python-gdal-library/'''


#############
# Functions #
#############
def transform_utm_to_wgs84(easting, northing, zone):
    utm_coordinate_system = osr.SpatialReference()

    # Set geographic coordinate system to handle lat/lon
    utm_coordinate_system.SetWellKnownGeogCS("WGS84")
    is_northern = northing > 0
    utm_coordinate_system.SetUTM(zone, is_northern)

    # Clone ONLY the geographic coordinate system
    wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS()

    # create transform component
    utm_to_wgs84_geo_transform = osr.CoordinateTransformation(utm_coordinate_system, wgs84_coordinate_system)  # (, )

    # returns lon, lat, altitude
    return utm_to_wgs84_geo_transform.TransformPoint(easting, northing, 0)


class WGS84Transform(object):
    def get_utm_zone(self, longitude):
        return (int(1 + (longitude + 180.0) / 6.0))

    def is_lat_northern(self, latitude):
        """
        Determines if given latitude is a northern for UTM
        """
        if (latitude < 0.0):
            return 0
        else:
            return 1

    def wgs84_to_utm(self, lon, lat):
        utm_coordinate_system = osr.SpatialReference()
        # Set geographic coordinate system to handle lat/lon
        utm_coordinate_system.SetWellKnownGeogCS("WGS84")
        utm_coordinate_system.SetUTM(self.get_utm_zone(lon), self.is_lat_northern(lat))

        # Clone ONLY the geographic coordinate system
        wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS()

        # create transform component
        wgs84_to_utm_geo_transform = osr.CoordinateTransformation(wgs84_coordinate_system,
                                                                  utm_coordinate_system)  # (, )
        # returns easting, northing, altitude
        return wgs84_to_utm_geo_transform.TransformPoint(lon, lat, 0)


def get_iterable_extent(*args):
    '''Returns list of minimum and maximum from lists/array input'''
    iterable_extent = list()
    for iter_object in args:
        iterable_extent.append(min(iter_object))
        iterable_extent.append(max(iter_object))
    return iterable_extent


def get_raster_size(min_x, min_y, max_x, max_y, cell_width, cell_height):
    """Determine the number of rows/columns given the bounds of the point
    data and the desired cell size"""

    cols = int((max_x - min_x) / cell_width)
    rows = int((max_y - min_y) / abs(cell_height))
    return cols, rows


def lonlat_to_pixel(lon, lat, inverse_geo_transform):
    """Translates the given lon, lat to the grid pixel coordinates
    in data array (zero start)"""
    wgs84_object = WGS84Transform()
    # transform to utm
    utm_x, utm_y, utm_z = wgs84_object.wgs84_to_utm(lon, lat)

    # apply inverse geo tranform
    pixel_x, pixel_y = gdal.ApplyGeoTransform(inverse_geo_transform, utm_x, utm_y)
    pixel_x = int(pixel_x) - 1  # adjust to 0 start for array
    pixel_y = int(pixel_y) - 1  # adjust to 0 start for array

    return pixel_x, abs(pixel_y)  # y pixel is likly a negative value given geo_transform


def create_raster(lons, lats, filename="montserrat-dem.vrt", output_format="MEM"):
    x_rotation = 0
    y_rotation = 0
    cell_width_meters = 15.0
    cell_height_meters = 15.0

    # retrieve bounds for point data
    min_lon, max_lon, min_lat, max_lat = get_iterable_extent(lons, lats)

    # Fa transformacions al sistema de coordenades
    # Set geographic coordinate system to handle lat/lon
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")

    # Set projected coordinate system  to handle meters
    wgs84_obj = WGS84Transform()
    srs.SetUTM(wgs84_obj.get_utm_zone(min_lon), wgs84_obj.is_lat_northern(max_lat))

    # create transforms for point conversion
    wgs84_coordinate_system = srs.CloneGeogCS()  # clone only the geographic coordinate system
    wgs84_to_utm_transform = osr.CoordinateTransformation(wgs84_coordinate_system, srs)
    utm_to_wgs84_transform = osr.CoordinateTransformation(srs, wgs84_coordinate_system)

    # convert bounds to UTM
    top_left_x, top_left_y, z = wgs84_obj.wgs84_to_utm(min_lon, max_lat)
    lower_right_x, lower_right_y, z = wgs84_obj.wgs84_to_utm(max_lon, min_lat)

    # Llegim el model d'elevacions (met[..].txt)
    dataset = gdal.Open(filename, gdal.GA_Update)
    # Llegim la transformacio del fitxer
    geo_transform = dataset.GetGeoTransform()
    # Assignem la projeccio
    dataset.SetProjection(srs.ExportToWkt())
    # Fem la inversa de la transformacio per passar de lat/lon a pixel
    inverse_geo_transform = gdal.InvGeoTransform(geo_transform)

    # agafem la banda raster del fitxer
    band = dataset.GetRasterBand(1)  # 1 == band index value

    eles = []

    for lon, lat in zip(lons, lats):  # zip: estructura de dades rollo map, iterem sobre els vectors lat i lon alhora
        pixel_x, pixel_y = lonlat_to_pixel(lon, lat, inverse_geo_transform)  # convertim lat/lon a pixel
        scanline = band.ReadAsArray(pixel_x, pixel_y, 1, 1, 1, 1)  # llegim el pixel al fitxer
        eles.append(scanline)

    # set dataset to None to "close" file
    dataset = None

    return eles


#################
# Main Function #
#################
# Llegim els punts del xml (osm)
# execusio del script

# busquem els punts nodes i posem les apltures

conn = psycopg2.connect(database=configuration_data["database"], user=configuration_data["user"],
                        password=configuration_data["password"], host=configuration_data["host"])

cursor = conn.cursor()
# cursor.execute('select public.update_node_way()')
# cursor.execute('select public.realitza_talls()')
# cursor.execute('delete from public.way_point n where Exists(select * from public.way_point n1 where n1.is_limit and n1.id_way =n.id_way and n.way_position>n1.way_position and n1.way_position!=1)')


div = 10000000
cursor.execute("SELECT pon.id, pon.lon::numeric/" + str(div) + " as lon, pon.lat::numeric/" + str(div) + " as lat "
                                                                                                         "FROM public.planet_osm_nodes pon,public.way_point wp "
                                                                                                         "where pon.id=wp.id_node");
points = cursor.fetchall()

print("Print each row and it's columns values")

objectPoints = []
# Afegim latitud i longitud de cada punt a dos vectors
for id, lon, lat in points:
    objectPoints.append({
        'id': id,
        'lat': float(lat),
        'lon': float(lon)
    })
# obtenim elevacions
print('create raster')
eles = create_raster([p['lon'] for p in objectPoints], [p['lat'] for p in objectPoints])

i = 0
print('set altitudes')

for p in objectPoints:
    if (eles[i] is not None):  # si tenim dades, afegim l'atribut (per saltar-nos els None)
        ele = eles[i][0, 0]
        q = "Update public.planet_osm_nodes SET height = " + str(ele) + " where id = " + str(p['id'])+';'
        cursor.execute(q)
        conn.commit()
    else:
        '''
        minDist=99999;
        for key in range(objectPoints):
            if(eles[i] is not None):
                if(minDist>distance([p['lat'],p['lon']],[objectPoints[key]['lat'],objectPoints[key]['lon']])):
                    minDist=distance([p['lat'],p['lon']],[objectPoints[key]['lat'],objectPoints[key]['lon']])
                    ele = eles[key][0, 0]
        '''
        q = "Update public.planet_osm_nodes SET height = 0 where id = " + str(p['id'])+';'
        cursor.execute(q)
        conn.commit()
    i = i + 1
cursor.close()


cursorWaysToSet = conn.cursor()
cursorNodesToSet = conn.cursor()

cursorWaysToSet.execute("SELECT wr.id_way, wr.id_self_key, osmw.tags"
	" FROM public.way_relation wr,public.planet_osm_ways osmw"
	" where osmw.id=wr.id_way;");
ways = cursorWaysToSet.fetchall()

objectPoints = []
# Afegim latitud i longitud de cada punt a dos vectors
for id_osm, id_ours, tags in ways:
    cursorNodesToSet.execute("SELECT wp.id_way, wp.id_node, wp.way_position, osm_n.lat, osm_n.lon, osm_n.height"
                    " FROM public.way_point wp, public.planet_osm_nodes osm_n"
                    " where id_way=" + str(id_ours) +" and wp.id_node=osm_n.id Order by wp.way_position;");
    points=cursorNodesToSet.fetchall();
    posRamp=0
    negRamp=0
    dist=0
    lastPoint=None
    lastPos=None
    for id_way, id_node, way_position, lat, lon, height in points:
        lat=lat/div
        lon=lon/div
        if(lastPoint==None):
            if(way_position!=1):
                print('eroooooooooooooooooooor'+id_way)
        else:
            if(lastPoint['height']>height):
                posRamp=lastPoint['height']-height
            else:
                negRamp=lastPoint['height']-height
            if(lastPos+1!=way_position):
                print('eroooooooooooooooooooor position'+id_way)
            distanceCursor = conn.cursor()
            distanceCursor.execute("select ST_Distance("
                                       "ST_SetSRID(ST_MakePoint("+str(lastPoint['lat'])+", "+str(lastPoint['lon'])+", "+str(lastPoint['height'])+"),4326)::geography,"
                                       "ST_SetSRID(ST_MakePoint("+str(lat)+", "+str(lon)+", "+str(height)+"),4326)::geography"
                                       ");")
            distanceSelector = distanceCursor.fetchone()
            dist=dist+distanceSelector[0]
        lastPos=way_position
        lastPoint={
            'lat':lat,
            'lon':lon,
            'height':height
        }
    found=0
    selectedTag=None
    for tag in higwaytags:
        if(tag in tags):
            selectedTag=tag
            ++found
    oneWayDirection=0
    if('oneway' in tags):
        index=tags.index('oneway')
        if(index<len(tags)-1):
            if(tags[index+1] in onewayDirTags.keys()):
                oneWayDirection=onewayDirTags[tags[index+1]]
            else:
                oneWayDirection=1
        else:
            oneWayDirection=1

    cursorUpdate = conn.cursor()
    cursorWaysToSet.execute("UPDATE public.way_relation"
	    " SET dist=" + str(dist) +", ramp_neg=" + str(negRamp) +","
        " ramp_pos=" + str(posRamp) +", oneway=" + str(oneWayDirection) +", highway_type='" + selectedTag +"'"
	    " WHERE id_self_key=" + str(id_ours) +";")
    conn.commit()

    if(found>1 or selectedTag==None):
        print(tags)
        break;

conn.close()
