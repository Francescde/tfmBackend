import xml.etree.ElementTree as ET
#'vehicles/DARRERES_POSICIONS.kml'

vehiclesSTR = ['walk', 'car', 'BRP', '4x4']
tipus_Vehicles = {
    '#w_grocP': 0,
    '#w_verdP': 0,
    '#w_grocC': 2,
    '#w_verdC': 2,
    '#w_groc': 3,
    '#w_verd': 3,
}

def getVehicleNameList():
    return vehiclesSTR

def extractPlacemarks(file):
    places=[]
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        if('Document' in str(child.tag)):
            for folder in child:
                if('Folder' in str(folder.tag)):
                    for placemark in folder:
                        #styleUrl
                        if('Placemark' in str(placemark)):
                            name=''
                            coorStr=''
                            coordinates=[]
                            tipus=''
                            for point in placemark:
                                #print(str(point))
                                if('name' in str(point)):
                                    name = point.text
                                if('styleUrl' in str(point)):
                                    tipus = point.text
                                if('Point' in str(point)):
                                    for coordinates in point:
                                        if('coordinates' in str(coordinates)):
                                            coorStr=coordinates.text
                            arrcor=coorStr.split(',')
                            coordinates=[arrcor[1],arrcor[0]]
                            places.append({
                                'name': name,
                                'coordinates': coordinates,
                                'type': tipus_Vehicles[tipus]
                            })
    return places