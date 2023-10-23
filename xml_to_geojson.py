# read xml file and transform into geojson file
# python xml_to_geojson.py -i <input_filename> -o <output_filename>

import argparse
import xmltodict
import simplejson

# useful functions
def hex2rgb(hexcode): # hexcode example: '#FF0840'
    r,g,b = int(hexcode[1:3],16),int(hexcode[3:5],16),int(hexcode[5:7],16)
    return [r,g,b]

# read in arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-i',help='geojson input filename')
parser.add_argument('-o',help='xml output filename')
args = parser.parse_args()

# make geojson from xml

# read in xml file
f = open(args.i, 'r')
# from the xml file, we can retrieve a dictionary
xml_dict = xmltodict.parse(f.read())


xml_polygons = xml_dict['ASAP_Annotations']['Annotations']['Annotation']
geojson_polygons = []

for xml_polygon in xml_polygons:
    name = xml_polygon['@PartOfGroup']
    color = xml_polygon['@Color']
    coords = []
    for coord in xml_polygon['Coordinates']['Coordinate']:
        coords.append([float(coord['@X']), float(coord['@Y'])])
    coords.append(coords[0])

    geojson_polygon = {'type':'Feature',
                       'id':'PathDetectionObject',
                       'geometry':{
                           'type': 'Polygon',
                           'coordinates': [coords]
                       },
                       'properties':{
                           'objectType': 'annotation',
                           'classification': {
                               'name': name,
                               'color': [244,250,88]
                           },
                           'color': hex2rgb(color)
                       }
                       }
    geojson_polygons.append(geojson_polygon)

geojson = {'type': 'FeatureCollection', 'features': geojson_polygons}

f = open(args.o, 'w')
f.write(simplejson.dumps(geojson,indent=4))
f.close()

print(f'geojson file {args.o} generated from xml file {args.i}')