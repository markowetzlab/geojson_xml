# Geojson XML Package
The two most commonly used histopathology annotation programs are ASAP, which uses the xml file format for annotations, and QuPath, which uses the geojson file format for annotations. Since both programs have their pros and cons, it is convenient to easily switch between the two formats.
## Converter 🔄
#### xml to geojson
`python geojson_to_xml.py -o <output_filename> -i <input_filename>`
#### geojson to xml
`python xml_to_geojson.py -o <output_filename> -i <input_filename>`

## Add color according to color dictionary :red_circle:
The dictionary has to be in quotation marks. The keys of the dictionary are the labels of the annotations that should be colored, the keys of the dictionary represent the colors either in hex code (starting with a #, e.g., `'#00FFA8'`), rgb (list of three numbers between 0 and 255, e.g., `[0,255,178]`), or just the name of the color (needs to be one of those: `'sky_blue', 'blue', 'turquoise', 'aquamarine', 'azure', 'dark_pink', 'red', 'fuchsia', 'apricot', 'dark_red', 'pink', 'apple_green', 'green', 'dark_green', 'amber', 'banana', 'blond', 'brown_orange', 'green_grey', 'blue_gray', 'blue_green', 'blue_violet', 'lavender', 'almond', 'gray', 'black', 'neon_green', 'neon_lilac', 'neon_orange', 'neon_pink'`)
In the terminal, the dictionary can be represented with e.g., `-d {'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}`
#### xml
`python xml_color_change.py -i <input_filename> -o <output_filename> -d <col_dict>`
#### geojson
`python geojson_color_change.py -i <input_filename> -o <output_filename> -d <col_dict>`

## Add tiles to figure out correct label threshold 🟥
The label threshold gives an idea of how big the part of the tile is that covers the annotation. The higher the threshold, the less tiles will be picked.
One input file is a pml file that was produced from the whole slide image and the xml annotation file.
The dictionary has to be in quotation marks. The keys of the dictionary are the labels of the annotations that should be colored, the keys of the dictionary represent the colors either in hex code (starting with a #, e.g., `'#00FFA8'`), rgb (list of three numbers between 0 and 255, e.g., `[0,255,178]`), or just the name of the color (needs to be one of those: `'sky_blue', 'blue', 'turquoise', 'aquamarine', 'azure', 'dark_pink', 'red', 'fuchsia', 'apricot', 'dark_red', 'pink', 'apple_green', 'green', 'dark_green', 'amber', 'banana', 'blond', 'brown_orange', 'green_grey', 'blue_gray', 'blue_green', 'blue_violet', 'lavender', 'almond', 'gray', 'black', 'neon_green', 'neon_lilac', 'neon_orange', 'neon_pink'`)
In the terminal, the dictionary can be represented with e.g., `-d {'unsure':'#009900', 'aberrant_positive_columnar':'blue', 'unspecific_stain':[255,180,0]}`
#### xml
`python xml_label_tiles.py -p <pml_file> -x <input_xml_file> -o <output_xml_file> -d <color_dict>`
#### geojson
`python geojson_label_tiles.py -p <pml_file> -g <input_geojson_file> -o <output_geojson_file> -d <color_dict>`

## Add tiles to figure out correct tissue threshold 🟪
The tissue threshold gives an idea of how big the part of the tile is that is covered by tissue. The higher the threshold, the less tiles will be picked.
One input file is a pml file that was produced from the whole slide image and the xml annotation file.
This is helpful, as for the inference, one only is interested in tiles which don't have stains but do contain mostly tissue.
The tissue level (a number between 0 and 100) is only important, if the method used is 'slidl'. Otherwise, the methods 'otsu' and 'triangle' are binary (True/False). We recommend to use the 'triangle' method with an artifact level of 0.3.
The color of the grid can either be represented in hex code (starting with a #, e.g., `'#00FFA8'`), rgb (list of three numbers between 0 and 255, e.g., `[0,255,178]`), or just the name of the color (needs to be one of those: `'sky_blue', 'blue', 'turquoise', 'aquamarine', 'azure', 'dark_pink', 'red', 'fuchsia', 'apricot', 'dark_red', 'pink', 'apple_green', 'green', 'dark_green', 'amber', 'banana', 'blond', 'brown_orange', 'green_grey', 'blue_gray', 'blue_green', 'blue_violet', 'lavender', 'almond', 'gray', 'black', 'neon_green', 'neon_lilac', 'neon_orange', 'neon_pink'`)
#### xml
`python xml_tissue_tiles.py -p <pml_file> -s <slide_file> -o <output_xml_file> -c <color> -t <tissue_level> -m <method> -a <artifact_level>`
#### geojson
`python xml_tissue_tiles.py -p <pml_file> -s <slide_file> -o <output_xml_file> -c <color> -t <tissue_level> -m <method> -a <artifact_level>`
