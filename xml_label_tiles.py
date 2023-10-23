# good to check whether label threshold is appropriate
# python xml_from_pml_tiles.py -p <pml_file> -x <input_xml_file> -s <slide_file> -o <output_xml_file> -d <color_dict> -l 0.05
# example dictionary: {'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}

import re
import argparse
from slidl.slide import Slide
import ast


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
parser.add_argument('-x',help='xml input filename')
parser.add_argument('-s',help='slide input filename', default=None)
parser.add_argument('-d',help='dictionary with labels as keys and rgb or hex or color names as values',type=str)
parser.add_argument('-o',help='xml output filename')
parser.add_argument('-l',help='label threshold (how big of a minimal area should the label annotation cover?), floating number between 0 and 1', default=0.01, type=float)
#parser.add_argument('-t',help='tissue threshold (how big of a minimal area should the tissue annotation cover?), floating number between 0 and 1', default=0.01, type=float)
args = parser.parse_args()

# read pml file
if not args.s:
	slidl_slide = Slide(args.p)
else:
	slidl_slide = Slide(args.p, newSlideFilePath=args.s)

# make dictionary of hex code
col_dict_messy = ast.literal_eval(args.d)
col_dict_clean = {}
for key,value in col_dict_messy.items():
    #print(key,value,type(value))
    if check_rgb(str(value)):
        col_dict_clean[key+'Overlap'] = rgb2hex(value)
        #print('rgb')
    elif check_hex(value):
        col_dict_clean[key+'Overlap'] = value.lower()
        #print('hex')
    elif value in colors_dict.keys():
        col_dict_clean[key+'Overlap'] = name2hex(value)
        #print('name')

labels = list(set(col_dict_clean.keys()).intersection(slidl_slide.tileDictionary[(0,0)].keys()))
new_dict = {}

for key,value in slidl_slide.tileDictionary.items():
    for label in labels:
        #if label in value.keys():
        if value[label] >= args.l:# and value['tissueLevel'] >= TISSUE_THRESHOLD:
            value['label'] = label.replace('Overlap','')
            new_dict[key] = value

xml_header = """<?xml version="1.0"?>\n<ASAP_Annotations>\n\t<Annotations>\n"""
xml_tail = "\t</Annotations>\n\t<AnnotationGroups>\n"

original_xml_filename = args.x #'/mnt/scratchc/fmlab/marker01/slides/Adam/p53/test_annotations/'+slidl_slide.slideFileName+'.xml'
f = open(original_xml_filename,'r')
original_xml = ['\t\t<Annotation Name='+i for i in f.read().split('<Annotations>')[1].split('</Annotations>')[0].split('<Annotation Name=')][1:]#.split('<ASAP_Annotations>')[1].split('<AnnotationGroups>')[0].split('<Annotation Name=')][1:]
colored_original_xml = []
for i in original_xml:
    label_ = re.findall(r'PartOfGroup="(.*?)"',i)[0]
    if label_+'Overlap' in labels:
        colored_original_xml.append(re.sub(r'Color="(.*?)"','Color="'+col_dict_clean[label_+'Overlap']+'"',i))
colored_original_xml = '\n'.join(colored_original_xml)

for key, value in col_dict_clean.items():
    key = key.replace('Overlap','')
    xml_tail = xml_tail+f"""\t\t<Group Name="{key}" PartOfGroup="None" Color="{value}">\n\t\t\t<Attributes />\n\t\t</Group>\n"""

xml_tail = xml_tail+'\t</AnnotationGroups>\n</ASAP_Annotations>'

xml_annotations = ""
num = 0

for key, value in new_dict.items():
    xml_annotations = (xml_annotations +
        "\t\t<Annotation Name=\""+str(round(value[value['label']+'Overlap'],3))+"\" Type=\"Polygon\" PartOfGroup=\""+value['label']+"\" Color=\"#F4FA58\">\n" +
        "\t\t\t<Coordinates>\n" +
        "\t\t\t\t<Coordinate Order=\"0\" X=\""+str(value['x'])+"\" Y=\""+str(value['y'])+"\" />\n" +
        "\t\t\t\t<Coordinate Order=\"1\" X=\""+str(value['x']+value['width'])+"\" Y=\""+str(value['y'])+"\" />\n" +
        "\t\t\t\t<Coordinate Order=\"2\" X=\""+str(value['x']+value['width'])+"\" Y=\""+str(value['y']+value['width'])+"\" />\n" +
        "\t\t\t\t<Coordinate Order=\"3\" X=\""+str(value['x'])+"\" Y=\""+str(value['y']+value['width'])+"\" />\n" +
        "\t\t\t</Coordinates>\n" +
        "\t\t</Annotation>\n")
    num += 1

with open(args.o, "w") as annotation_file:
    annotation_file.write(xml_header + colored_original_xml + xml_annotations + xml_tail)

print(f'colored tiles xml file {args.o} generated from original xml file {args.x} and pml file {args.p} with a label threshold of {args.l}')
