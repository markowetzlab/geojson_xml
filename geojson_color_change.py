# change colors of geojson file according to input dictionary
# if annotation label not in dictionary, then color will be yellow [244,250,88]
# python geojson_color_change.py -i <input_filename> -o <output_filename> -d <color_dictionary>
# e.g., geojson_color_change.py -i example.geojson -o example_colored.geojson -d "{'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}"
# if hexcode, then it needs to start with '#'
# if color name, then it needs to be one of those: ['sky_blue', 'blue', 'turquoise', 'aquamarine', 'azure', 'dark_pink', 'red', 'fuchsia', 'apricot', 'dark_red', 'pink', 'apple_green', 'green', 'dark_green', 'amber', 'banana', 'blond', 'brown_orange', 'green_grey', 'blue_gray', 'blue_green', 'blue_violet', 'lavender', 'almond', 'gray', 'black', 'neon_green', 'neon_lilac', 'neon_orange', 'neon_pink']

import argparse
import simplejson
import re

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
parser.add_argument('-i',help='geojson input filename',type=str)
parser.add_argument('-o',help='colored geojson output filename', type=str)
parser.add_argument('-d',help='string of dictionary with labels as keys and rgb or hex or color names as values',type=str)
args = parser.parse_args()

# make dictionary of [r,g,b]
col_dict_messy = eval(args.d)
col_dict_clean = {}
for key,value in col_dict_messy.items():
    #print(key,value,type(value))
    if check_rgb(str(value)):
        col_dict_clean[key] = value
        #print('rgb')
    elif check_hex(value):
        col_dict_clean[key] = hex2rgb(value)
        #print('hex')
    elif value in colors_dict.keys():
        col_dict_clean[key] = name2rgb(value)
        #print('name')

# read geojson file
f = open(args.i, 'r')
geojson_dict_old = eval(f.read())

geojson_polygons = geojson_dict_old['features']
geojson = []

for geojson_polygon in geojson_polygons:
    label = geojson_polygon['properties']['classification']['name']
    if label in col_dict_clean.keys():
        geojson_polygon['properties']['color'] = col_dict_clean[label]
    else:
        geojson_polygon['properties']['color'] = [244,250,88] # yellow
    geojson.append(geojson_polygon)

geojson = {'type': 'FeatureCollection', 'features': geojson}

f = open(args.o, 'w')
f.write(simplejson.dumps(geojson,indent=4))
f.close()

print(f'colored geojson file {args.o} generated from geojson file {args.i}')