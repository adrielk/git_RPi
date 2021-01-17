#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import time
import sys
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image


host_name = '192.168.1.229'    # Change this to your Raspberry Pi IP address
host_port = 8000
led_pin = 11

gif_folder_name = "dank_gifs"
os.chdir(os.getcwd()+"/"+gif_folder_name)

#juicy list comprehension
img_list = [filename for filename in os.listdir(os.getcwd()) if filename.endswith(".gif")]

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

def loop_screen():
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

class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """

    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command 
            'curl -I http://server-ip-address:port' 
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        """ do_GET() can be tested using curl command 
            'curl http://server-ip-address:port' 
        """
        html = '''
            <html>
            <body style="width:960px; margin: 20px auto;">
            <h1>Welcome to Adriel's Raspberry Pi</h1>
            <p>Current GPU temperature is {}</p>
            <form action="/" method="POST">
                Turn LED :
                <input type="submit" name="submit" value="On">
                <input type="submit" name="submit" value="Off">
            </form>
            </body>
            </html>
        '''
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def do_POST(self):
        """ do_POST() can be tested using curl command 
            'curl -d "submit=On" http://server-ip-address:port' 
        """
        content_length = int(self.headers['Content-Length'])    # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")   # Get the data
        post_data = post_data.split("=")[1]    # Only keep the value
        
        # GPIO setup
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(led_pin,GPIO.OUT)

        if post_data == 'On':
            loop_screen()
            #GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)
        print("LED is {}".format(post_data))
        self._redirect('/')    # Redirect back to the root url

# def setup():
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(led_pin, GPIO.OUT)
#     GPIO.output(led_pin, GPIO.HIGH)
#     print('using pin%d'%led_pin)


if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))
    #setup()
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()