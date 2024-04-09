from openslide import OpenSlide
import json
import xmltodict
import os
import argparse

"""
The difference between the geojson file and the ndp file is that they have both different units (ndp: nanometers, geojson: pixels) and different coordinate systems (ndp: centre left, geojson: top left corner). 
Therefore, we need to convert the coordinates from the geojson file to the ndp file.
"""

def arg_parse():
    parser = argparse.ArgumentParser(description='geojson to ndp file that can be opened with NDP Viewer')
    parser.add_argument('--geojson', type=str, help='geojson file path')
    parser.add_argument('--ndpi', type=str, help='ndpi file path')
    parser.add_argument('--output', type=str, help='output file path')
    return parser.parse_args()

def convert_pixels_to_nanometers(pixel_coords, conversion_factor=220.88708252341402):
    nanometer_coords = []
    for coord in pixel_coords:
        nanometer_coords.append([int(coord[0] * conversion_factor), int(coord[1] * conversion_factor)])
    return nanometer_coords

def convert_nanometers_to_pixels(nanometer_coords, conversion_factor=220.88708252341402):
    pixel_coords = []
    for coord in nanometer_coords:
        pixel_coords.append([int(coord[0] / conversion_factor), int(coord[1] / conversion_factor)])
    return pixel_coords

def convert_coords_to_ndp(coords, x_offset, y_offset, conversion_factor):
    ndp_coords = []
    for coord in coords:
        ndp_coords.append([int((coord[0] * conversion_factor) - x_offset), int((coord[1] * conversion_factor) - y_offset)])
    return ndp_coords

# Read in arguments from command line
args = arg_parse()
geojson_file = args.geojson
ndpi_file = args.ndpi
output_file = args.output

if not os.path.exists(geojson_file):
    raise FileNotFoundError(f'geojson file {geojson_file} does not exist')

if not os.path.exists(ndpi_file):
    raise FileNotFoundError(f'ndpi file {ndpi_file} does not exist')

if output_file is None:
    output_file = os.path.splitext(ndpi_file)[0] + '.ndpi.ndpa'
    print(f'output file not specified, saving to {output_file}')

# Read the geojson file
with open(geojson_file, 'r') as f:
    geojson = json.load(f)

# Read the ndpi file
slide = OpenSlide(ndpi_file)
# Get the offset for x and y
x_offset = int(slide.properties.get('hamamatsu.XOffsetFromSlideCentre'))
y_offset = int(slide.properties.get('hamamatsu.YOffsetFromSlideCentre'))
# Get the conversion factor
conversion_factor = float(slide.properties.get('openslide.mpp-x'))*1000
# Get the dimensions of the slide
x_ref, y_ref = convert_pixels_to_nanometers([(slide.dimensions[0]/2, slide.dimensions[1]/2)], conversion_factor=conversion_factor)[0]
# Calculate the x and y offset
x_offset = x_ref - x_offset
y_offset = y_ref - y_offset


geojson_polygons = geojson['features']

ndp_view_list = []

for ind, geojson_polygon in enumerate(geojson_polygons):
    geojson_coords = geojson_polygon['geometry']['coordinates'][0]
    
    # Calculate x_mean and y_mean
    x_mean = convert_pixels_to_nanometers([(int(sum([i[0] for i in geojson_coords]) / len(geojson_coords)), 0)])[0][0]
    y_mean = convert_pixels_to_nanometers([(int(sum([i[1] for i in geojson_coords]) / len(geojson_coords)), 0)])[0][0]

    # Convert the coordinates to ndp
    ndp_coords = convert_coords_to_ndp(geojson_coords, x_offset, y_offset, conversion_factor)

    # Make point list
    pointlist = {'point': [{'x': str(int(i[0])), 'y': str(int(i[1]))} for i in ndp_coords]}

    # Make the xml
    ndp_view_list.append(
        {
            '@id': str(ind+1),
            'title': 'Annotation '+str(ind+1),
            'details': 'These are the details of Annotation '+str(ind+1),
            'coordformat': 'nanometers',
            'lens': '3.628447',
            'x': str(x_mean),
            'y': str(y_mean),
            'z': '0',
            'showtitle': '0',
            'showhistogram': '0',
            'showlineprofile': '0',
            'annotation': {
                '@type': 'freehand',
                '@displayname': 'AnnotateFreehandLine',
                '@color': '#00ff00',
                'measuretype': '0',
                'closed': '1',
                'pointlist': pointlist
            }
        }
    )

# Make the xml
xml = {'annotations': {'ndpviewstate': ndp_view_list}}

# Write the xml to file
with open(output_file, 'w') as f:
    f.write(xmltodict.unparse(xml, pretty=True))

print(f'ndp file {output_file} generated from geojson file {geojson_file}')