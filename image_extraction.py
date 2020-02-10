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


image_path = 'PNG_compressed'
mei_path_split = '180829_split/mei'
mei_path_unsplit = '180831_unsplit/mei'
salz_path = 'salz'
mapping_file = 'img_name_to_cantus_mapping.csv'
output_path = 'output_img'
output_txt = 'output_xml'
# os.system(f'rm -rf { output_path }')
# os.system(f'rm -rf { output_txt }')

mapping = pd.read_csv(mapping_file)
entries = mapping.shape[0]

os.system(f'rm -rf { output_path }')

if not os.path.isdir(output_path):
    os.mkdir(output_path)

if not os.path.isdir(output_txt):
    os.mkdir(output_txt)

with open(f'output.txt', 'w') as f:
    f.write('file_name,type\n')
    for i, mei_file in enumerate(sorted(os.listdir(salz_path))):
        if mei_file.endswith('.DS_Store'):
            continue
        elif i > entries - 1:
            break
        mapped_file = mapping.iloc[i]['filename']
        # print(image_path + '/' + mei_file[:-4] + '.png')
        img = Image.open(image_path + '/' + mapped_file + '.png')
        # print(mei_path_unsplit + '/' + mei_file)
        contents = open(salz_path + '/' + mei_file, 'r', encoding='utf8').read()
        soup = BeautifulSoup(contents, 'xml')
        # staffs = soup.find_all('staff')
        neumes = soup.find_all(['neume', 'clef', 'custos'])
        zones = soup.find_all('zone')
        i = 0
        for zone in zones:
            fac = zone['xml:id']
            if int(zone['lrx']) - int(zone['ulx']) > 10:
                for neume in neumes:
                    neume_type = ''
                    if neume['facs'] == fac:
                        zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
                        zone_img.save(f'{ output_path }/{ mei_file[:-4] }_{ i }.png')
                        neume_type = 'hold'
                        if neume.has_attr('name'):
                            if neume.findChild().has_attr('inclinatum'):
                                neume_type = 'inclinatum'
                            else:
                                neume_type = neume['name']
                        elif neume.has_attr('shape'):
                            neume_type = 'clef.' + neume['shape'].lower()
                        elif neume.has_attr('pname'):
                            neume_type = 'custos'

                        f.write(f'{ mei_file[:-4] }_{ i },{ neume_type }\n')
                        i += 1

        # comments = list(soup.find_all(string=lambda text: isinstance(text, Comment)))
        #
        # staff_facs = []
        neumes_facs = []
        clef_facs = []
        # clef_shapes = []
        custos_facs = []
        # clean_comments = []
        #
        # for staff in staffs:
        #     staff_facs.append(staff['facs'])
        # for clef in clefs:
        #     clef_facs.append(clef['facs'])
        #     clef_shapes.append(clef['shape'])
        # for c in custos:
        #     custos_facs.append(c['facs'])
        # for comment in comments:
        #     comment = re.sub(r'\.[a-zA-Z][0-9]\.', ', ', comment)
        #     for neume in comment.split(', '):
        #         clean_comments.append(neume)
        # print('Neumes:', len(clean_comments) + len(clefs) + len(custos))
        # # oblique repeat removal
        #
        # temp_zone = BeautifulSoup('<zone lrx="-1" lry="-1" ulx="-1" uly="-1" xml:id="q-5d0f64d9-f3ba-4ddd-bc4c-9192cdbe0d1f"/>').zone
        #
        # for zone in soup.find_all('zone'):
        #     if (temp_zone['ulx'] == zone['ulx'] and temp_zone['lry'] == zone['lry']) or zone['xml:id'] in staff_facs:
        #         zone['delete'] = 1
        #     temp_zone = zone
        #
        # for zone in soup.find_all('zone'):
        #     if zone.has_attr('delete'):
        #         zone.decompose()
        #
        # zones = soup.find_all('zone')
        # print('Zones:', len(zones))
        #
        #
        #
        # # print(type(comments))
        # # REGEX COMMENT CLEANUP: \.[a-zA-Z][0-9]\. (might not need)
        #
        #
        #
        # # if not os.path.isdir(output_path + '/' + mei_file[:-4]):
        # #     os.mkdir(output_path + '/' + mei_file[:-4])
        # zone_count = 0
        # nc_inc = 0
        #
        # for zone in zones:
        #     fac = zone['xml:id']
        #     if fac in clef_facs:
        #         ind = clef_facs.index(fac)
        #         if clef_shapes[ind] == 'C':
        #             f.write(f'{ mei_file[:-4] }_{ zone_count }.png,clef.c\n')
        #         else:
        #             f.write(f'{ mei_file[:-4] }_{ zone_count }.png,clef.f\n')
        #     elif fac in custos_facs:
        #         f.write(f'{ mei_file[:-4] }_{ zone_count }.png,custos\n')
        #     else:
        #         f.write(f'{ mei_file[:-4] }_{ zone_count }.png,{ clean_comments[nc_inc] }\n')
        #         nc_inc += 1
        #     zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
        #     zone_img.save(f'{ output_path }/{ mei_file[:-4] }_{ zone_count }.png')
        #     zone_count += 1
        # tree = ET.parse(mei_path + '/' + mei_file)
