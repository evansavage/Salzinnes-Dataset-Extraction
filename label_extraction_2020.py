import os
import sys
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
from bs4 import Comment
import re
from datetime import datetime
import pickle

print('Subfolder types [sS] or txt file types [tT]?')
data_arrangement = input()

if data_arrangement not in ['s','S','t','T']:
    sys.exit()

date = datetime.now().strftime('%Y_%m_%d')

image_path = '20_06_11_Sal_Ein_img'
mei_path_unsplit = '20_06_14_ground_truth'
output_path = 'output_img_' + date

# Ein_dim = [4872,6496]
# Sal_dim = [4414,6993]
#
# Sal_Ein_ratio = np.divide(Sal_dim, Ein_dim)
# Ein_Sal_ratio = np.divide(Ein_dim, Sal_dim)
#
# Sal_Ein_slope = (Sal_dim[1] - Ein_dim[1]) / (Sal_dim[0] - Ein_dim[0])
#
# intercept = Sal_dim[1] - Sal_Ein_slope * Sal_dim[0]

os.system(f'rm -rf { output_path }')

if not os.path.isdir(output_path):
    os.mkdir(output_path)

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



if data_arrangement in ['t','T']:
    file_name_arr = []
    int_label_arr = []

    with open(f'output_{ date }.txt', 'w') as f:
        f.write('file_name,type,ulx,uly,lrx,lry,position,pitch,oct,type_string,pos_string\n')
        for i, mei_file in enumerate(sorted(os.listdir(mei_path_unsplit))):
            if mei_file.endswith('.DS_Store'):
                continue
            if i == stop_check:
                break
            if 'Ein-' in mei_file:
                manu = 'Ein'
            else:
                manu = 'Sal'
            img = Image.open(image_path + '/' + mei_file[:-17] + '.png')
            contents = open(mei_path_unsplit + '/' + mei_file, 'r', encoding='utf8').read()
            soup = BeautifulSoup(contents, 'xml')

            # Contains all punctums, inclinatums, obliques, clefs, custos
            glyphs = soup.find_all(['clef', 'custos'])
            neumes = soup.find_all('syllable')
            current_pitches = []
            # Contains all coordinates of above glyphs
            zones = soup.find_all('zone')
            layer = soup.find('layer')
            # print(glyphs)
            # Loop through every zone and get clefs and custos
            j = 0
            # for zone in zones:
            #     fac = zone['xml:id']
            #     # Not worth looking into if zone coords are too thin
            #     if int(zone['lrx']) - int(zone['ulx']) > 1:
            #         for glyph in glyphs:
            #             glyph_type = ''
            #             # Have found a facsimile to inspect
            #             if glyph['facs'][1:] == fac:
            #                 # If custos/clef, can grab coords, o.w. the syllable needs to be broken down
            #                 if glyph.name == 'clef':
            #                     neume_type = f"{ glyph.name }.{ glyph['shape'].lower() }"
            #                     if neume_type == 'clef.f':
            #                         add_dim = clef_f_dim
            #                     else:
            #                         add_dim = clef_c_dim
            #                 elif glyph.name == 'custos':
            #                     neume_type = glyph.name
            #                     add_dim = custos_dim
            #                 width = int(zone['lrx']) - int(zone['ulx']) + add_dim[0] + add_dim[1]
            #                 height = int(zone['lry']) - int(zone['uly']) + add_dim[2] + add_dim[3]
            #                 if width > w_cancel_dim:
            #                     w_cancel += 1
            #                     continue
            #                 if height > h_cancel_dim:
            #                     h_cancel += 1
            #                     continue
            #                 blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
            #                 zone_img = img.crop((int(zone['ulx'])-add_dim[0],int(zone['uly'])-add_dim[2],int(zone['lrx'])+ add_dim[1],int(zone['lry'])+add_dim[3]))
            #                 blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
            #                 blank_image.save(f'{ output_path }/{ mei_file[:-15] }_{ j }.png')
            #                 h_sum += height
            #                 w_sum += width
            #                 total_img += 1
            #                 if width > w_max:
            #                     w_max = width
            #                 if height > h_max:
            #                     h_max = height
            #                 f.write(f'{ mei_file[:-4] }_{ j },{ neume_arr.index(neume_type) }\n')
            #                 file_name_arr.append(f'{ mei_file[:-4] }_{ j }.png')
            #                 int_label_arr.append(neume_arr.index(neume_type))
            #                 # print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
            #                 j += 1

            # NEW METHOD ASSUMING 'READING ORDER' OF TAGS INSIDE <layer>
            for glyph in layer.find_all(recursive=False):
                if glyph.name == 'sb':
                    continue
                elif glyph.name in ['clef', 'custos']:
                    zone = soup.find('zone', {"xml:id": glyph['facs'][1:]})
                    if glyph.name == 'clef': # update pitch encoding, position saved for clef should be line it's centered on
                        neume_type = f"{ glyph.name }.{ glyph['shape'].lower() }"
                        if neume_type == 'clef.f':
                            if manu == 'Ein': add_dim = clef_f_dim_ein
                            else: add_dim = clef_f_dim
                            add_dim = clef_f_dim
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
                            # octave = -1
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
                        # staff_pos = current_pitches.index(pitch)
                        octave = int(glyph['oct'])
                        staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))
                    width = int(zone['lrx']) - int(zone['ulx']) + add_dim[0] + add_dim[1]
                    height = int(zone['lry']) - int(zone['uly']) + add_dim[2] + add_dim[3]
                    if width > w_cancel_dim:
                        w_cancel += 1
                        continue
                    if height > h_cancel_dim:
                        h_cancel += 1
                        continue
                    blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
                    final_coords = [int(zone['ulx'])-add_dim[0],int(zone['uly'])-add_dim[2],int(zone['lrx'])+ add_dim[1],int(zone['lry'])+add_dim[3]]
                    zone_img = img.crop((final_coords))
                    blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
                    blank_image.save(f'{ output_path }/{ mei_file[:-17] }_{ j }.png')
                    h_sum += height
                    w_sum += width
                    total_img += 1
                    if width > w_max:
                        w_max = width
                    if height > h_max:
                        h_max = height
                    f.write(f'{ mei_file[:-17] }_{ j },{ neume_arr.index(neume_type) },{ final_coords[0] },{ final_coords[1]},{ final_coords[2]},{ final_coords[3]},{ staff_pos },{ pitch },{ octave },{ neume_type },{ position_array[staff_pos] }\n')
                    file_name_arr.append(f'{ mei_file[:-17] }_{ j }.png')
                    int_label_arr.append(neume_arr.index(neume_type))
                    # print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
                    j += 1
                elif glyph.name == 'syllable': # NEED TO GET ALL NESTED NEUME COMPONENTS
                    # syl_iter = 0 # NEED TO ADVANCE EXTRA WITH OBLIQUE
                    nc_arr = glyph.find_all('nc')
                    if len(nc_arr) > 1: # OBLIQUE
                        # print('yes')
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
                        staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))
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
                        staff_pos = current_pitches.index(next(x for x in current_pitches if x == [pitch,octave]))

                    width = coords[2] - coords[0] + add_dim[0] + add_dim[1]
                    height = coords[3] - coords[1] + add_dim[2] + add_dim[3]
                    # if width > w_cancel_dim:
                    #     w_cancel += 1
                    #     continue
                    # if height > h_cancel_dim:
                    #     h_cancel += 1
                    #     continue
                    blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
                    final_coords = [coords[0]-add_dim[0],coords[1]-add_dim[2],coords[2]+ add_dim[1],coords[3]+add_dim[3]]
                    zone_img = img.crop((final_coords))
                    blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
                    blank_image.save(f'{ output_path }/{ mei_file[:-17] }_{ j }.png')
                    h_sum += height
                    w_sum += width
                    total_img += 1
                    if width > w_max:
                        w_max = width
                    if height > h_max:
                        h_max = height
                    f.write(f'{ mei_file[:-17] }_{ j },{ neume_arr.index(neume_type) },{ final_coords[0] },{ final_coords[1] },{ final_coords[2] },{  final_coords[3] },{ staff_pos },{ pitch },{ octave },{ neume_type },{ position_array[staff_pos] }\n')
                    file_name_arr.append(f'{ mei_file[:-17] }_{ j }.png')
                    int_label_arr.append(neume_arr.index(neume_type))
                    # syl_iter += 1
                    j += 1

            # Now need to look into each syllable to find neume components (names in comment)
            # for neume in neumes:
            #     dirty_types = neume.find(string=lambda text: isinstance(text, Comment)).replace(', ', '.').split('.')
            #     nc_types = []
            #     lig_toggle = 0
            #     # Remove entries from nc_arr that are not neume components ('u2', 'd2', etc.)
            #     for str in dirty_types:
            #         if not str.startswith(('u', 'd', 's1')):
            #             nc_types.append(str)
            #     # print(nc_types)
            #     nc_arr = neume.find_all('nc')
            #     nc_arr_filter = []
            #     # Remove redundant ligature nc tags
            #     for nc in nc_arr:
            #         if nc.has_attr('ligature'):
            #             lig_toggle += 1
            #             lig_toggle %= 2
            #             if lig_toggle == 0:
            #                 nc_arr_filter.append(nc)
            #         else:
            #             nc_arr_filter.append(nc)
            #     # Find corresponding coordinates based on facs
            #     for k, nc in enumerate(nc_arr_filter):
            #         fac = nc['facs']
            #         for zone in zones:
            #             neume_type = ''
            #             # Found the corrsponding zone w/ coords
            #             if zone['xml:id'] == fac:
            #                 neume_type = nc_types[k]
            #                 width = int(zone['lrx']) - int(zone['ulx'])
            #                 height = int(zone['lry']) - int(zone['uly']) + 30
            #                 if width > w_cancel_dim:
            #                     w_cancel += 1
            #                     continue
            #                 if height > h_cancel_dim:
            #                     h_cancel += 1
            #                     continue
            #                 blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
            #                 zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
            #                 # For placement: (ulx, uly)
            #                 blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
            #                 blank_image.save(f'{ output_path }/{ mei_file[:-4] }_{ j }.png')
            #                 f.write(f'{ mei_file[:-4] }_{ j },{ neume_arr.index(neume_type) }\n')
            #                 file_name_arr.append(f'{ mei_file[:-4] }_{ j }.png')
            #                 int_label_arr.append(neume_arr.index(neume_type))
            #
            #                 h_sum += height
            #                 w_sum += width
            #                 total_img += 1
            #                 if width > w_max:
            #                     w_max = width
            #                 if height > h_max:
            #                     h_max = height
            #                 print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
            #                 j += 1
    pickle_dict = {}
    pickle_dict['Filenames'] = file_name_arr
    pickle_dict['Labels'] = int_label_arr
    pickle.dump(pickle_dict, open(f'label_map_{ date }.pickle', 'wb'))
elif data_arrangement in ['s','S']:
    for i, mei_file in enumerate(sorted(os.listdir(mei_path_unsplit))):
        if mei_file.endswith('.DS_Store'):
            continue
        if i == stop_check:
            break
        img = Image.open(image_path + '/' + mei_file[:-4] + '.png')
        contents = open(mei_path_unsplit + '/' + mei_file, 'r', encoding='utf8').read()
        soup = BeautifulSoup(contents, 'xml')

        # Contains all punctums, inclinatums, obliques, clefs, custos
        glyphs = soup.find_all(['clef', 'custos'])
        neumes = soup.find_all('syllable')

        # Contains all coordinates of above glyphs
        zones = soup.find_all('zone')

        # Loop through every zone and get clefs and custos
        j = 0
        for zone in zones:
            fac = zone['xml:id']
            # Not worth looking into if zone coords are too thin
            if int(zone['lrx']) - int(zone['ulx']) > 10:
                for glyph in glyphs:
                    glyph_type = ''
                    # Have found a facsimile to inspect
                    if glyph['facs'] == fac:
                        # If custos/clef, can grab coords, o.w. the syllable needs to be broken down
                        if glyph.name == 'clef':
                            neume_type = f"{ glyph.name }.{ glyph['shape'].lower() }"
                        elif glyph.name == 'custos':
                            neume_type = glyph.name
                        if not os.path.isdir(output_path + f'/{ neume_type }'):
                            os.mkdir(output_path + f'/{ neume_type }')
                        width = int(zone['lrx']) - int(zone['ulx'])
                        height = int(zone['lry']) - int(zone['uly']) + 30
                        if width > w_cancel_dim:
                            w_cancel += 1
                            continue
                        if height > h_cancel_dim:
                            h_cancel += 1
                            continue
                        blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
                        zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
                        blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
                        blank_image.save(f'{ output_path }/{neume_type}/{ mei_file[:-4] }_{ j }.png')
                        h_sum += height
                        w_sum += width
                        total_img += 1
                        if width > w_max:
                            w_max = width
                        if height > h_max:
                            h_max = height
                        print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
                        j += 1

        # Now need to look into each syllable to find neume components (names in comment)
        for neume in neumes:
            dirty_types = neume.find(string=lambda text: isinstance(text, Comment)).replace(', ', '.').split('.')
            nc_types = []
            lig_toggle = 0
            # Remove entries from nc_arr that are not neume components ('u2', 'd2', etc.)
            for str in dirty_types:
                if not str.startswith(('u', 'd', 's1')):
                    nc_types.append(str)
            # print(nc_types)
            nc_arr = neume.find_all('nc')
            nc_arr_filter = []
            # Remove redundant ligature nc tags
            for nc in nc_arr:
                if nc.has_attr('ligature'):
                    lig_toggle += 1
                    lig_toggle %= 2
                    if lig_toggle == 0:
                        nc_arr_filter.append(nc)
                else:
                    nc_arr_filter.append(nc)
            # Find corresponding coordinates based on facs
            for k, nc in enumerate(nc_arr_filter):
                fac = nc['facs']
                for zone in zones:
                    neume_type = ''
                    # Found the corrsponding zone w/ coords
                    if zone['xml:id'] == fac:
                        neume_type = nc_types[k]
                        width = int(zone['lrx']) - int(zone['ulx'])
                        height = int(zone['lry']) - int(zone['uly']) + 30
                        if width > w_cancel_dim:
                            w_cancel += 1
                            continue
                        if height > h_cancel_dim:
                            h_cancel += 1
                            continue
                        if not os.path.isdir(output_path + f'/{ neume_type }'):
                            os.mkdir(output_path + f'/{ neume_type }')
                        blank_image = Image.new('RGB', (blank_w, blank_h), (255, 255, 255))
                        zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
                        # For placement: (ulx, uly)
                        blank_image.paste(zone_img, (int((blank_w - width) / 2), int((blank_h - height) / 2)))
                        blank_image.save(f'{ output_path }/{neume_type}/{ mei_file[:-4] }_{ j }.png')

                        h_sum += height
                        w_sum += width
                        total_img += 1
                        if width > w_max:
                            w_max = width
                        if height > h_max:
                            h_max = height
                        print(f'Saving { mei_file[:-4] }_{ j }.png', f'Avg dim: { w_sum / total_img } by { h_sum / total_img }', f'Max width: { w_max }', f'Max height: { h_max }')
                        j += 1



print(f'\nCancelled width: { w_cancel }, Cancelled height: { h_cancel }')
