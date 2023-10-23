# good to check whether label threshold is appropriate
# python xml_tissue_tiles.py -p <pml_file> -s <slide_file> -o <output_xml_file> -c <color> -t <tissue_level> -m <method> -a <artifact_level>
# color: #009900, blue, or [255,180,0] --> can be either hex code, name from colors_dict or rgb [0-255]
# method: 'slidl', 'otsu', or 'triangle'

import re
import argparse
from slidl.slide import Slide


# useful functions
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

# read in arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-p',help='pml input filename')
parser.add_argument('-s',help='slide input filename', default=None)
parser.add_argument('-c',help='color of grid, either as name, hex code, or rgb code', type=str, default='neon_lilac')
parser.add_argument('-o',help='xml output filename')
parser.add_argument('-t',help='tissue threshold (how big of a minimal area should the tissue annotation cover?), floating number between 0 and 1', default=80, type=float)
parser.add_argument('-a',help='tissue threshold (how big of a maximal area should the artifact annotation cover (stains,...)?), floating number between 0 and 1', default=0.3, type=float)
parser.add_argument('-m',help='method of extracting only tiles with tissue, "slidl", "otsu" or "triangle". "otsu" and "triangle" are binary, so the tissue threshold is not used', default='slidl')
args = parser.parse_args()

# read pml file
if not args.s:
	slidl_slide = Slide(args.p)
else:
	slidl_slide = Slide(args.p, newSlideFilePath=args.s)

input_color = args.c
# convert color into hex code
if check_rgb(input_color):
	color = rgb2hex(input_color)
	#print('rgb')
elif check_hex(input_color):
	color = input_color.lower()
	#print('hex')
elif input_color in colors_dict.keys():
	color = name2hex(input_color)
	#print('name')
else:
	print('Unable to process input color. Therefore, the grid color will be the default color, lilac.')

new_dict = {}

method = args.m
tissue_level = args.t
artifact_level = args.a

if method == 'slidl':
	for key,value in slidl_slide.tileDictionary.items():
	    if value['foregroundLevel'] <= tissue_level and value['artifactLevel'] >= artifact_level:
		    new_dict[key] = value
elif method == 'otsu':
	for key,value in slidl_slide.tileDictionary.items():
	    if value['foregroundOtsu'] and value['artifactLevel'] >= artifact_level:
		    new_dict[key] = value
elif method == 'triangle':
	for key,value in slidl_slide.tileDictionary.items():
	    if value['foregroundTriangle'] and value['artifactLevel'] >= artifact_level:
		    new_dict[key] = value

xml_header = """<?xml version="1.0"?>\n<ASAP_Annotations>\n\t<Annotations>\n"""

xml_tail = "\t</Annotations>\n\t<AnnotationGroups>\n"
xml_tail = xml_tail+f"""\t\t<Group Name="Tissue" PartOfGroup="None" Color="{color}">\n\t\t\t<Attributes />\n\t\t</Group>\n"""
xml_tail = xml_tail+'\t</AnnotationGroups>\n</ASAP_Annotations>'

xml_annotations = ""
num = 0


for key, value in new_dict.items():
	annotation_name = str(round(value['foregroundLevel'],3)) if method=='slidl' else 'Annotation '+str(num)
	xml_annotations = (xml_annotations +
	"\t\t<Annotation Name=\""+annotation_name+"\" Type=\"Polygon\" PartOfGroup=\"Tissue\" Color=\""+color+"\">\n" +
	"\t\t\t<Coordinates>\n" +
	"\t\t\t\t<Coordinate Order=\"0\" X=\""+str(value['x'])+"\" Y=\""+str(value['y'])+"\" />\n" +
	"\t\t\t\t<Coordinate Order=\"1\" X=\""+str(value['x']+value['width'])+"\" Y=\""+str(value['y'])+"\" />\n" +
	"\t\t\t\t<Coordinate Order=\"2\" X=\""+str(value['x']+value['width'])+"\" Y=\""+str(value['y']+value['width'])+"\" />\n" +
	"\t\t\t\t<Coordinate Order=\"3\" X=\""+str(value['x'])+"\" Y=\""+str(value['y']+value['width'])+"\" />\n" +
	"\t\t\t</Coordinates>\n" +
	"\t\t</Annotation>\n")
	num += 1

with open(args.o, "w") as annotation_file:
    annotation_file.write(xml_header + xml_annotations + xml_tail)

print(f'colored tiles xml file {args.o} generated from pml file {args.p} with a tissue threshold of {args.t} using the method {args.m}')
