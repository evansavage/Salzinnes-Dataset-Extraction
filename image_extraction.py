import os
import sys
import numpy as np
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
output_path = 'output_img'
output_txt = 'output_xml'
os.system(f'rm -rf { output_path }')
os.system(f'rm -rf { output_txt }')

if not os.path.isdir(output_path):
    os.mkdir(output_path)
if not os.path.isdir(output_txt):
    os.mkdir(output_txt)

for mei_file in sorted(os.listdir(mei_path_unsplit)):
    if mei_file.endswith('.DS_Store'):
        continue
    print(image_path + '/' + mei_file[:-4] + '.png')
    img = Image.open(image_path + '/' + mei_file[:-4] + '.png')
    print(mei_path_unsplit + '/' + mei_file)
    contents = open(mei_path_unsplit + '/' + mei_file, 'r', encoding='utf8')
    soup = BeautifulSoup(contents, 'xml')
    staffs = soup.find_all('staff')
    clefs = soup.find_all('clef')
    custos = soup.find_all('custos')
    comments = list(soup.find_all(string=lambda text: isinstance(text, Comment)))

    staff_facs = []
    clef_facs = []
    clef_shapes = []
    custos_facs = []
    clean_comments = []

    for staff in staffs:
        staff_facs.append(staff['facs'])
    for clef in clefs:
        clef_facs.append(clef['facs'])
        clef_shapes.append(clef['shape'])
    for c in custos:
        custos_facs.append(c['facs'])
    for comment in comments:
        comment = re.sub(r'\.[a-zA-Z][0-9]\.', ', ', comment)
        for neume in comment.split(', '):
            clean_comments.append(neume)
    print('Neumes:', len(clean_comments) + len(clefs) + len(custos))
    # oblique repeat removal

    temp_zone = BeautifulSoup('<zone lrx="-1" lry="-1" ulx="-1" uly="-1" xml:id="q-5d0f64d9-f3ba-4ddd-bc4c-9192cdbe0d1f"/>').zone

    for zone in soup.find_all('zone'):
        if (temp_zone['ulx'] == zone['ulx'] and temp_zone['lry'] == zone['lry']) or zone['xml:id'] in staff_facs:
            zone['delete'] = 1
        temp_zone = zone

    for zone in soup.find_all('zone'):
        if zone.has_attr('delete'):
            zone.decompose()

    zones = soup.find_all('zone')
    print('Zones:', len(zones))



    # print(type(comments))
    # REGEX COMMENT CLEANUP: \.[a-zA-Z][0-9]\. (might not need)



    if not os.path.isdir(output_path + '/' + mei_file[:-4]):
        os.mkdir(output_path + '/' + mei_file[:-4])
    zone_count = 0
    nc_inc = 0
    with open(f'{ output_txt }/{ mei_file[:-4] }.txt', 'w') as f:
        f.write('file_name,type\n')
        for zone in zones:
            fac = zone['xml:id']
            if fac in clef_facs:
                ind = clef_facs.index(fac)
                if clef_shapes[ind] == 'C':
                    f.write(f'{ mei_file[:-4] }_{ zone_count }.png,clef.c\n')
                else:
                    f.write(f'{ mei_file[:-4] }_{ zone_count }.png,clef.f\n')
            elif fac in custos_facs:
                f.write(f'{ mei_file[:-4] }_{ zone_count }.png,custos\n')
            else:
                f.write(f'{ mei_file[:-4] }_{ zone_count }.png,{ clean_comments[nc_inc] }\n')
                nc_inc += 1
            zone_img = img.crop((int(zone['ulx']),int(zone['uly'])-15,int(zone['lrx']),int(zone['lry'])+15))
            zone_img.save(f'{ output_path }/{ mei_file[:-4] }/{ mei_file[:-4] }_{ zone_count }.png')
            zone_count += 1
    # tree = ET.parse(mei_path + '/' + mei_file)
