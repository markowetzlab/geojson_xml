# read geojson file and transform into xml file
# pyhton geojson_to_xml.py -i <input_filename> -o <output_filename>

import argparse
import xmltodict

# useful functions
def rgb2hex(rgb_list): # rgb_list example: [255,0,3]
    r,g,b = rgb_list
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

# read in arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-i',help='geojson input filename')
parser.add_argument('-o',help='xml output filename')
args = parser.parse_args()

# read in geojson file
f = open(args.i, 'r')
geojson_dict = eval(f.read())

# make xml from geojson
geojson_polygons = geojson_dict['features']

xml_polygons, group_dict, group_list = [], {}, []

for ind,geojson_polygon in enumerate(geojson_polygons):
    coords = geojson_polygon['geometry']['coordinates'][0] # [[42800, 2800], [43200, 2800], [43200, 3200], [42800, 3200], [42800, 2800]]
    # last coord is same as first one, therefore we can remove it
    if coords[0] == coords[-1]:
        coords = coords[:-1]
    try:
        color = geojson_polygon['properties']['color']
    except KeyError:
        try:
            color = geojson_polygon['properties']['classification']['color']
        except KeyError:
            color = '#F4FA58'
    label = geojson_polygon['properties']['classification']['name']
    group_dict[label] = color

    coords_dict = []
    for ind_, coord in enumerate(coords):
        coords_dict.append({'@Order':str(ind_), '@X':str(coord[0]), '@Y':str(coord[1])})

    xml_polygon = {'@Name': 'Annotation '+str(ind),
                   '@Type': 'Polygon',
                   '@PartOfGroup': label,
                   '@Color': str(rgb2hex(color)).upper(),
                   'Coordinates': {'Coordinate': coords_dict}}
    
    xml_polygons.append(xml_polygon)

for group,col in group_dict.items():
    group_list.append({'@Name': group, '@PartOfGroup': None, '@Color': col, 'Attributes': None})

xml = {'ASAP_Annotations':{'Annotations':{'Annotation':xml_polygons},
                           'AnnotationGroups':{'Group':group_list}}}

xml = xmltodict.unparse(xml, pretty=True)

# save xml file
f = open(args.o, 'w')
f.write(xml)
f.close()


print(f'xml file {args.o} generated from geojson file {args.i}')
