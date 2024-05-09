import PIL as pil
from PIL import Image
import csv
import math

#data
countries = ['E', 'PT', 'DK', 'LT', 'LU', 'HR', 'LV', 'UA', 'HU', 'MC', 'UK', 'MD', 'ME', 'IE', 'MK', 'EE', 'AD', 'IM',
             'MT', 'EL', 'IS', 'IT', 'VA', 'AL', 'ES', 'AT', 'JE', 'RO', 'NL', 'BA', 'NO', 'RS', 'BE', 'FI', 'BG', 'FO', 
             'FR', 'SE', 'SI', 'BY', 'SK', 'SM', 'GG', 'GI', 'CH', 'CY', 'CZ', 'PL', 'LI', 'TR']

dataset = open('processed_1km.csv', 'r')
csvreader = csv.reader(dataset)
header = []
header=next(csvreader)
hold = 1411021
print(header)

def scale_pop_to_color(pop):
    blue = ((int(pop))*255)//1000
    #print(blue)
    return blue
#img

image = Image.new('RGB', (20000, 20000), (0,0,0))
print('image done!')
for row in csvreader:
    if row[7] not in ['UA', 'BY', 'TR']:
        x = (int(row[13]))//600
        y = (int(row[6]))//-600
        if x < 50000 and y < 50000:
            image.putpixel((x, y), (255-scale_pop_to_color(row[4]), 255-scale_pop_to_color(row[4]), 255))

image.show()
