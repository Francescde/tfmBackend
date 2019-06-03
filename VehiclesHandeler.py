import json

with open('configurationFiles/vehiclesSpeed.json') as json_file:
	vehicles = json.load(json_file)


'''

	"path" : "inf",
	"residential" : "50",
	"track" : {
		"grade1": "35",
		"grade2": "25",
		"grade3": "20",
		"grade4": "15",
		"grade5": "10"
		},
	"service" : "50",
	"primary" : "80",
	"unclassified" : "50",
	"motorway" : "90",
	"secondary" : "70",
	"motorway_link" : "70",
	"tertiary" : "50",
	"primary_link": "60",
	"secondary_link": "30",
	"tertiary_link" : "15"

'''
