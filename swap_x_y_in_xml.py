## swap x and y position of xml file


import xmltodict
import argparse

parser = argparse.ArgumentParser(description='Swap x and y position of xml file')
parser.add_argument('-i', type=str, help='xml input filename')
parser.add_argument('-o', type=str, help='xml output filename')
args = parser.parse_args()

# read in xml file
f = open(args.i, 'r')
# from the xml file, we can retrieve a dictionary
xml_dict = xmltodict.parse(f.read())

xml_polygons = xml_dict['ASAP_Annotations']['Annotations']['Annotation']

new_xml_polygons = []
for xml_polygon in xml_polygons:
    new_coords = []
    for coord in xml_polygon['Coordinates']['Coordinate']:
        # change x and y position
        new_coords.append({'@Order':coord['@Order'], '@X':coord['@Y'], '@Y':coord['@X']})
    new_dict = xml_polygon.copy()
    new_dict.pop('Coordinates')
    new_dict['Coordinates'] = {}
    new_dict['Coordinates']['Coordinate'] = new_coords
    new_xml_polygons.append(new_dict)

xml_dict['ASAP_Annotations']['Annotations'].pop('Annotation')
xml_dict['ASAP_Annotations']['Annotations']['Annotation'] = new_xml_polygons

# write to new xml file
f = open(args.o, 'w')
f.write(xmltodict.unparse(xml_dict, pretty=True))
f.close()

print(f'swapped x and y to xml file {args.o} generated from xml file {args.i}')