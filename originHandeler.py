from kmlHandeler import extractPlacemarks, getVehicleNameList

def giveVehiclesStr():
    return getVehicleNameList()


def give_origins(file):
    ends = [{
            'coordinates': [41.7410791,1.849642],
            'name': 'Manresa',
            'type': -1
        },{
            'coordinates': [41.4987656,1.9079489],
            'name': 'Martorell',
            'type': -1
        },{
            'coordinates': [41.5891303,1.6078417],
            'name': 'Igualada',
            'type': -1
        },{
            'coordinates': [41.5687856,1.8242247],
            'name': 'Collbato',
            'type': -1
        },{
            'coordinates': [41.6656828,1.6830365],
            'name': 'Castellfollit del Boix',
            'type': -1
        },{
            'coordinates': [41.5619597,1.9614527],
            'name': 'Viladecavalls',
            'type': -1
        }]

    vehicles = extractPlacemarks(file)
    for vehicle in vehicles:
        ends.append(vehicle)
    return ends