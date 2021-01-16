#!/usr/bin/env python
import time
import sys
import os
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

#TO DO: 
#Allow images to be sent through google hangouts and automically displayed
#Webscrape fairly square gifs only on giphy
#Input and process images live (retrive from database that's updated live)

# if len(sys.argv) < 2:
#     sys.exit("Require an image argument")
# else:
#     image_file = sys.argv[1]

gif_folder_name = "dank_gifs"
os.chdir(os.getcwd()+"/"+gif_folder_name)

#juicy list comprehension
img_list = [filename for filename in os.listdir(os.getcwd()) if filename.endswith(".gif")]

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.gpio_slowdown =4
options.brightness = 50

matrix = RGBMatrix(options = options)

loop_num = 3
while(True):
    random.shuffle(img_list)
    for gif in img_list:
        image = Image.open(gif)
        loop_times = loop_num if image.n_frames < 50 else 1
        #loop_times = loop_num if image.n_frames < 50 else 1
        for i in range(0, loop_times):
            for frame in range(0, image.n_frames):
                image.seek(frame)
                image_copy = image.convert('RGB').copy().resize((64,64))
                matrix.SetImage(image_copy)
                time.sleep(0.07)



try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)