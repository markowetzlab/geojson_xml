# good to check whether label threshold is appropriate
# python geojson_from_pml_tiles.py -p <pml_file> -g <input_geojson_file> -o <output_geojson_file> -d <color_dict>
# example dictionary: {'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}


import re
import argparse
from slidl.slide import Slide
import geojson
import ast

# useful functions
def check_rgb(input_str): # "[0, 255, 178]"
    pattern = r'\[\d{1,3}, \d{1,3}, \d{1,3}\]'
    match = re.match(pattern, input_str)
    if match:
        return True
    return False

def check_hex(input_str): # '#AAFF80'
    pattern = r'#[0-9a-fA-F]{6}'
    match = re.match(pattern, input_str)
    if match:
        return True
    return False

def hex2rgb(hexcode): # hexcode example: '#FF0840'
    r,g,b = int(hexcode[1:3],16),int(hexcode[3:5],16),int(hexcode[5:7],16)
    return [r,g,b]

colors_dict = {
    # blue
    'sky_blue': '#7CB9E8', 'blue': '#0000FF', 'turquoise': '#00FFFF', 'aquamarine': '#7FFFD4', 'azure': '#007FFF',
    # red/pink
    'dark_pink': '#AB274F', 'red': '#D3212D', 'fuchsia': '#915C83', 'apricot': '#FBCEB1', 'dark_red': '#7C0A02', 'pink': '#DA1884',
    # green
    'apple_green': '#8DB600', 'green': '#87A96B', 'dark_green': '#568203',
    # yellow/brown
    'amber': '#FFBF00', 'banana': '#FAE7B5', 'blond': '#FAF0BE', 'brown_orange': '#C46210',
    # mix
    'green_grey': '#8F9779', 'blue_gray': '#6699CC', 'blue_green': '#0D98BA', 'blue_violet': '#8A2BE2',
    # other
    'lavender': '#B284BE', 'almond': '#EFDECD', 'gray': '#B2BEB5', 'black': '#000000',
    # neon
    'neon_green': '#66FF00', 'neon_lilac': '#D891EF', 'neon_orange': '#FFAA1D', 'neon_pink': '#FF55A3'}

def name2rgb(colorname): # colorname example: 'blue' # color name must be in colors_dict
    hexcode = colors_dict[colorname]
    r,g,b = int(hexcode[1:3],16),int(hexcode[3:5],16),int(hexcode[5:7],16)
    return [r,g,b]

# read in arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-p',help='pml input filename')
parser.add_argument('-g',help='geojson input filename')
parser.add_argument('-d',help='dictionary with labels as keys and rgb or hex or color names as values',type=str)
parser.add_argument('-o',help='geojson output filename')
parser.add_argument('-l',help='label threshold (how big of a minimal area should the label annotation cover?), floating number between 0 and 1', default=0.001)
#parser.add_argument('-t',help='tissue threshold, floating number ')
args = parser.parse_args()

# read pml file
slidl_slide = Slide(args.p)

# make dictionary of [r,g,b]
col_dict_messy = ast.literal_eval(args.d)
col_dict_clean = {}
for key,value in col_dict_messy.items():
    #print(key,value,type(value))
    if check_rgb(str(value)):
        col_dict_clean[key+'Overlap'] = value
        #print('rgb')
    elif check_hex(value):
        col_dict_clean[key+'Overlap'] = hex2rgb(value)
        #print('hex')
    elif value in colors_dict.keys():
        col_dict_clean[key+'Overlap'] = name2rgb(value)
        #print('name')

print(col_dict_clean)

labels = list(set(col_dict_clean.keys()).intersection(slidl_slide.tileDictionary[(0,0)].keys()))
new_dict = {}

for key,value in slidl_slide.tileDictionary.items():
    for label in labels:
        #if label in value.keys():
        if value[label] >= args.l:# and value['tissueLevel'] >= TISSUE_THRESHOLD:
            value['label'] = label.replace('Overlap','')
            new_dict[key] = value

# read geojson file
f = open(args.g, 'r')
geojson_dict_old = eval(f.read())

geojson_polygons = geojson_dict_old['features']
geojson_annotations = []

for geojson_polygon in geojson_polygons:
    label = geojson_polygon['properties']['classification']['name']
    if label+'Overlap' in labels:
        geojson_polygon['properties']['color'] = col_dict_clean[label+'Overlap']
        geojson_annotations.append(geojson_polygon)

for key, value in new_dict.items():
        geojson_annotations.append({
                "type": "Feature",
                "id": "PathDetectionObject",
                "geometry": {
                "type": "Polygon",
                "coordinates": [
                                [
                                        [value['x'], value['y']],
                                        [value['x']+value['width'], value['y']],
                                        [value['x']+value['width'], value['y']+value['width']],
                                        [value['x'], value['y']+value['width']],
                                        [value['x'], value['y']]
                                ]
                        ]
                },
                "properties": {
                        "objectType": "annotation",
                        "classification": {
                                "name": value['label'],
                                "color": [244,250,88]
                        },
                        "color": col_dict_clean[value['label']+'Overlap']
        }
})
        
json_annotations = {"type": "FeatureCollection", "features":geojson_annotations}
with open(args.o, "w") as annotation_file:
        geojson.dump(json_annotations, annotation_file, indent=4)

print(f'colored tiles geojson file {args.o} generated from original geojson file {args.g} and pml file {args.p} with a label threshold of {args.l}')