import os
import sys
import numpy as np
import pandas as pd
import cv2
from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
from bs4 import Comment
import re
from datetime import datetime
import pickle

image_path = '20_06_11_Sal_Ein_img'
mei_path_unsplit = '20_06_14_ground_truth'

h_sum = 0
w_sum = 0
h_max = 0
w_max = 0
total_img = 0

stop_check = 1000000000

w_cancel = 0
h_cancel = 0
w_cancel_dim = 256
h_cancel_dim = 256

blank_w = w_cancel_dim
blank_h = h_cancel_dim

neume_arr = ['clef.c', 'clef.f',
             'custos', 'inclinatum', 'oblique2', 'oblique3',
             'oblique4', 'punctum', 'virga']
letter_array = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

position_array = ['s1','l1','s2','l2','s3','l3','s4','l4','s5']

#  FOR CLEF ENCODING, LINE IS WHERE THE REFERENCE PITCH IS FOUND, NESTED ENCODING FOR OCTAVE INCLUSION

clef_c_line4 = [['c',2],['d',2],['e',2],['f',2],['g',2],['a',2],['b',2],['c',3],['d',3]]
clef_c_line3 = [['e',2],['f',2],['g',2],['a',2],['b',2],['c',3],['d',3],['e',3],['f',3]]
clef_c_line2 = [['g',2],['a',2],['b',2],['c',3],['d',3],['e',3],['f',3],['g',3],['a',3]]

clef_f_line4 = [['f',2],['g',2],['a',2],['b',2],['c',3],['d',3],['e',3],['f',3],['g',3]]
clef_f_line3 = [['a',2],['b',2],['c',3],['d',3],['e',3],['f',3],['g',3],['a',3],['b',3]]
clef_f_line2 = [['c',3],['d',3],['e',3],['f',3],['g',3],['a',3],['b',3],['c',4],['d',4]]

# DIMENSION ARRAYS SALZINNES [left,right,top,bottom]

clef_c_dim = [0,0,70,40]
clef_f_dim = [5,30,70,35]
custos_dim = [10,0,40,20]
inc_dim = [5,5,35,10]
ob2_dim = [0,0,25,5]
ob3_dim = [0,0,25,5]
ob4_dim = [0,0,25,5]
punc_dim = [0,0,20,0]
virga_dim = [0,0,0,0]

# DIMENSION ARRAYS EINSIEDELN [left,right,top,bottom]

clef_c_dim_ein = [5,5,70,40]
clef_f_dim_ein = [5,30,90,35]
custos_dim_ein = [10,-10,100,0]
inc_dim_ein = [0,0,30,0]
ob2_dim_ein = [5,0,20,0]
ob3_dim_ein = [5,0,20,0]
ob4_dim_ein = [5,0,20,0]
punc_dim_ein = [5,5,30,5]
virga_dim_ein = [5,5,20,80]

print('Index [0-29]')
page_index = int(input())
mei_file = sorted(os.listdir(mei_path_unsplit))[page_index]
if 'Ein-' in mei_file:
    manu = 'Ein'
else:
    manu = 'Sal'
img = Image.open(image_path + '/' + mei_file[:-17] + '.png').convert("RGBA")
draw = ImageDraw.Draw(img)
contents = open(mei_path_unsplit + '/' + mei_file, 'r', encoding='utf8').read()
soup = BeautifulSoup(contents, 'xml')
layer = soup.find('layer')
font = ImageFont.truetype("arial.ttf",size=15)
print(mei_file)
color_cycle = [(255,0,0),(0,255,0),(0,0,255)]
color_iter = 0
for glyph in layer.find_all(recursive=False):
    # if glyph.name == 'sb':
    #     zone = soup.find('zone', {"xml:id": glyph['facs'][1:]})
    #     draw.rectangle((int(zone['ulx']),int(zone['uly']),int(zone['lrx']),int(zone['lry'])))
    #     draw.text((int(zone['ulx'])+20,int(zone['uly'])+20), glyph['n'], font=font,fill=(255,0,0))
    if glyph.name == 'sb':
        continue
    elif glyph.name in ['clef', 'custos']:
        zone = soup.find('zone', {"xml:id": glyph['facs'][1:]})
        if glyph.name == 'clef': # update pitch encoding, position saved for clef should be line it's centered on
            neume_type = f"{ glyph.name }.{ glyph['shape'].lower() }"
            if neume_type == 'clef.f':
                if manu == 'Ein': add_dim = clef_f_dim_ein
                else: add_dim = clef_f_dim
                # add_dim = clef_f_dim
                if glyph['line'] == "2":
                    current_pitches = clef_f_line2
                    staff_pos = 3
                elif glyph['line'] == "3":
                    current_pitches = clef_f_line3
                    staff_pos = 5
                elif glyph['line'] == "4":
                    current_pitches = clef_f_line4
                    staff_pos = 7
                pitch = 'clef'
            else:
                if manu == 'Ein': add_dim = clef_c_dim_ein
                else: add_dim = clef_c_dim
                if glyph['line'] == "2":
                    current_pitches = clef_c_line2
                    staff_pos = 3
                elif glyph['line'] == "3":
                    current_pitches = clef_c_line3
                    staff_pos = 5
                elif glyph['line'] == "4":
                    current_pitches = clef_c_line4
                    staff_pos = 7
                pitch = 'clef'
            octave = -1
        elif glyph.name == 'custos':
            if manu == 'Ein': add_dim = custos_dim_ein
            else: add_dim = custos_dim
            neume_type = glyph.name
            # add_dim = custos_dim
            pitch = glyph['pname']
            octave = int(glyph['oct'])
            # staff_pos = current_pitches.index(pitch)
            staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))
            print(staff_pos, pitch, octave, glyph['facs'][1:],current_pitches)
        # width = int(zone['lrx']) - int(zone['ulx']) + add_dim[0] + add_dim[1]
        # height = int(zone['lry']) - int(zone['uly']) + add_dim[2] + add_dim[3]
        # if width > w_cancel_dim:
        #     w_cancel += 1
        #     continue
        # if height > h_cancel_dim:
        #     h_cancel += 1
        #     continue
        final_coords = [int(zone['ulx'])-add_dim[0],int(zone['uly'])-add_dim[2],int(zone['lrx'])+ add_dim[1],int(zone['lry'])+add_dim[3]]
        draw.rectangle((final_coords))
        draw.text((final_coords[0]-10,final_coords[1]-40), neume_type, font=font,fill=color_cycle[color_iter])
        draw.text((final_coords[0]-10,final_coords[1]-20), position_array[staff_pos], font=font,fill=color_cycle[color_iter])
        color_iter += 1
        color_iter %= 3

        # print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
        # j += 1
    elif glyph.name == 'syllable': # NEED TO GET ALL NESTED NEUME COMPONENTS
        # syl_iter = 0 # NEED TO ADVANCE EXTRA WITH OBLIQUE
        nc_arr = glyph.find_all('nc')
        if len(nc_arr) > 1: # OBLIQUE
            print('yes')
            zone = soup.find('zone', {"xml:id": nc_arr[0]['facs'][1:]})
            zone2 = soup.find('zone', {"xml:id": nc_arr[1]['facs'][1:]})
            coords = [int(zone['ulx']), int(zone['uly']), int(zone2['lrx']), int(zone2['lry'])]
            zone_rel = [nc_arr[0]['pname'],int(nc_arr[0]['oct'])]
            zone2_rel = [nc_arr[1]['pname'],int(nc_arr[1]['oct'])]
            if current_pitches.index(zone_rel) - current_pitches.index(zone2_rel) == 1:
                neume_type = 'oblique2'
                if manu == 'Ein': add_dim = ob2_dim_ein
                else: add_dim = ob2_dim
            elif current_pitches.index(zone_rel) - current_pitches.index(zone2_rel) == 2:
                neume_type = 'oblique3'
                if manu == 'Ein': add_dim = ob3_dim_ein
                else: add_dim = ob3_dim
            else:
                neume_type = 'oblique4'
                if manu == 'Ein': add_dim = ob4_dim_ein
                else: add_dim = ob4_dim
            pitch = nc_arr[0]['pname']
            octave = int(nc_arr[0]['oct'])
            # staff_pos = current_pitches.index(pitch)
            staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))
            print(staff_pos, pitch, octave, nc_arr[0]['facs'][1:], current_pitches)
        else:
            nc = nc_arr[0]
            zone = soup.find('zone', {"xml:id": nc['facs'][1:]})
            if nc.has_attr('tilt'): # inclinatum / virga
                if nc['tilt'] == 'se':
                    neume_type = 'inclinatum'
                    if manu == 'Ein': add_dim = inc_dim_ein
                    else: add_dim = inc_dim
                else:
                    neume_type = 'virga'
                    if manu == 'Ein': add_dim = virga_dim_ein
                    else: add_dim = virga_dim
            # elif nc.has_attr('ligated'): # need new bounding box coords
            #     zone2 = soup.find('zone', {"xml:id": nc_arr[syl_iter+1]['facs'][1:]})
            #     # TO-DO: ADD_DIM BASED ON TYPE OF OBLIQUE
            #     coords = [int(zone['ulx']), int(zone['uly']), int(zone2['lrx']), int(zone2['lry'])]
            #     neume_type = 'oblique2'
            #     add_dim = ob2_dim
            #     syl_iter += 1
            else:
                neume_type = 'punctum'
                if manu == 'Ein': add_dim = punc_dim_ein
                else: add_dim = punc_dim
            coords = [int(zone['ulx']), int(zone['uly']), int(zone['lrx']), int(zone['lry'])]
            pitch = nc['pname']
            octave = int(nc['oct'])
            # staff_pos = current_pitches.index(pitch)
            staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))
            print(staff_pos, pitch, octave, nc['facs'][1:], current_pitches)

        width = coords[2] - coords[0] + add_dim[0] + add_dim[1]
        height = coords[3] - coords[1] + add_dim[2] + add_dim[3]
        # if width > w_cancel_dim:
        #     w_cancel += 1
        #     continue
        # if height > h_cancel_dim:
        #     h_cancel += 1
        #     continue
        # blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
        final_coords = [coords[0]-add_dim[0],coords[1]-add_dim[2],coords[2]+ add_dim[1],coords[3]+add_dim[3]]
        draw.rectangle((final_coords))
        draw.text((final_coords[0]-10,final_coords[1]-40), neume_type, font=font,fill=color_cycle[color_iter])
        draw.text((final_coords[0]-10,final_coords[1]-20), position_array[staff_pos], font=font,fill=color_cycle[color_iter])
        color_iter += 1
        color_iter %= 3
        # syl_iter += 1
        # j += 1

img.show()
