# change colors of xml file according to input dictionary
# if annotation label not in dictionary, then color will be yellow [244,250,88]
# python xml_color_change.py -i <input_filename> -o <output_filename> -d <color_dictionary>
# e.g., xml_color_change.py -i example.geojson -o example_colored.geojson -d {'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}
# if hexcode, then it needs to start with '#'
# if color name, then it needs to be one of those: ['sky_blue', 'blue', 'turquoise', 'aquamarine', 'azure', 'dark_pink', 'red', 'fuchsia', 'apricot', 'dark_red', 'pink', 'apple_green', 'green', 'dark_green', 'amber', 'banana', 'blond', 'brown_orange', 'green_grey', 'blue_gray', 'blue_green', 'blue_violet', 'lavender', 'almond', 'gray', 'black', 'neon_green', 'neon_lilac', 'neon_orange', 'neon_pink']

import argparse
import re
import xmltodict
import ast

# useful functions
class DictError(Exception):
    pass

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

def rgb2hex(rgb_list): # rgb_list example: [255,0,3]
    r,g,b = rgb_list
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

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

def name2hex(colorname): # colorname example: 'blue' # color name must be in colors_dict
    return colors_dict[colorname]

# read in arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-i',help='geojson input filename',type=str)
parser.add_argument('-o',help='colored geojson output filename', type=str)
parser.add_argument('-d',help='dictionary with labels as keys and rgb or hex or color names as values',type=str)
args = parser.parse_args()

# make dictionary of hex code
col_dict_messy = ast.literal_eval(args.d)
col_dict_clean = {}
for key,value in col_dict_messy.items():
    #print(key,value,type(value))
    if check_rgb(str(value)):
        col_dict_clean[key] = rgb2hex(value)
        #print('rgb')
    elif check_hex(value):
        col_dict_clean[key] = value
        #print('hex')
    elif value in colors_dict.keys():
        col_dict_clean[key] = name2hex(value)
        #print('name')
    else:
        raise DictError(f'Values in dictionary must either be in [r,g,b] format with numbers ranging from 0 to 255, or in hexcode format starting with # or one of the following color names: {colors_dict.keys()}')

# read in xml file
f = open(args.i, 'r')
# from the xml file, we can retrieve a dictionary
xml_dict = xmltodict.parse(f.read())

xml_polygons = xml_dict['ASAP_Annotations']['Annotations']['Annotation']
poly_list = []

for xml_polygon in xml_polygons:
    label = xml_polygon['@PartOfGroup']
    if label in col_dict_clean.keys():
        xml_polygon['@Color'] = col_dict_clean[label]
    else:
        xml_polygon['@Color'] = '#F4FA58' # yellow
    poly_list.append(xml_polygon)


xml_groups = xml_dict['ASAP_Annotations']['AnnotationGroups']['Group']
group_list = []

for xml_group in xml_groups:
    label = xml_group['@Name']
    if label in col_dict_clean.keys():
        xml_group['@Color'] = col_dict_clean[label]
    else:
        xml_group['@Color'] = '#F4FA58' # yellow
    group_list.append(xml_group)

xml = {'ASAP_Annotations':{'Annotations':{'Annotation':poly_list},
                           'AnnotationGroups':{'Group':group_list}}}

xml = xmltodict.unparse(xml, pretty=True)

# save xml file
f = open(args.o, 'w')
f.write(xml)
f.close()

print(f'colored xml file {args.o} generated from xml file {args.i}')