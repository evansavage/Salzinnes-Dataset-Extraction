import os
import sys
import numpy as np
import cv2
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
from bs4 import Comment
import re
import random

################################################################################
# IMPORTANT INFO (20-02-10 update)
# - use 'output_img_191023' images and 'output_nc_split_191023' for making pages


print('How many staffs do you want on a page?')
num_staffs = int(input())

page_width = 2000
page_height = 3000
top_offset = 200
bottom_offset = 500
margin_left = 200
margin_right = 200
staff_spacing = 100
staff_image = Image.open('fake_staff_lines.png', 'r')

neume_path = 'output_img_191023/'
neume_info = pd.read_csv('output_nc_split_191023.txt')
neume_info = neume_info.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
# print(neume_info)


staff_width_orig, staff_height_orig = staff_image.size

# df.loc[df['column_name'].isin(some_values)]

neumes = neume_info.loc[~neume_info['type'].isin(['clef.c', 'clef.f', 'custos'])]
clefs = neume_info.loc[neume_info['type'].isin(['clef.c', 'clef.f'])]
custos_arr = neume_info.loc[neume_info['type'] == 'custos']
print(custos_arr)
staff_scale = 100 / staff_height_orig
# staff_image.thumbnail((staff_width_orig*staff_scale, staff_height_orig*staff_scale), Image.ANTIALIAS)
blank_image = Image.new('RGBA', (page_width, page_height), (232, 228, 220, 255))
staff_coords = []
for i in range(num_staffs):
    if top_offset + int(0.33 * i * staff_width_orig*staff_scale) > page_height - bottom_offset:
        break
    neume_name = random.choice(neume_info['file_name'])
    neume_image = Image.open(neume_path + neume_name, 'r')
    neume_image = neume_image.crop((0,15, neume_image.size[0], neume_image.size[1] - 15))

    staff_scale_height = staff_scale * random.uniform(0.93, 1.07)
    staff_scale_width = random.uniform(0.97, 1.03)
    staff_place = staff_image.resize((int(staff_scale_width * (page_width - margin_left - margin_right)), int(staff_height_orig*staff_scale_height)), Image.ANTIALIAS)
    w, h = staff_place.size
    pos_offset = int(h / 6)
    margin_left_offset = random.randint(-10,10)
    blank_image.paste(staff_place, (margin_left + margin_left_offset , top_offset + int(0.33 * i * staff_width_orig*staff_scale)), mask=staff_place)
    num_neumes = random.randint(15, 30)
    for j in range(num_neumes):
        if j == 0: #
            choice = clefs.sample(n=1)
            choice_file, choice_type = choice.iloc[0]
            n_place = random.choice([0, 2, 4])
            scale = 2/3 + 0.05
        elif j == num_neumes - 1:
            choice = custos_arr.sample(n=1)
            choice_file, choice_type = choice.iloc[0]
            n_place = random.randint(0,8)
            scale = 1/3
        else:
            choice = neumes.sample(n=1)
            choice_file, choice_type = choice.iloc[0]
            if choice_type == 'oblique2':
                n_place = random.randint(0,7)
                scale = 1/2
            elif choice_type == 'oblique3':
                n_place = random.randint(0,6)
                scale = 2/3
            elif choice_type == 'oblique4':
                n_place = random.randint(0,5)
                scale = 5/6
            else:
                n_place = random.randint(0,8)
                scale = 1/3
        n_image = Image.open(neume_path + choice_file)
        n_image = n_image.crop((0,15, n_image.size[0], n_image.size[1] - 15))
        n_ratio = n_image.size[0] / n_image.size[1]
        n_image = n_image.resize((int(scale*h*n_ratio), int(scale*h)), Image.ANTIALIAS)
        blank_image.paste(n_image, (margin_left + margin_left_offset + int(j * w / num_neumes), top_offset + int(0.33 * i * staff_width_orig*staff_scale) + int(-2*pos_offset + n_place*pos_offset) + random.randint(-5,5)))

    # print(w, h, pos_offset)
    # blank_image.paste(neume_image, (random.randint(0,page_width), random.randint(0, page_height)))


blank_image.show()
cv2.waitKey()
