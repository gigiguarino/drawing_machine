#!/usr/bin/env python
from scipy import ndimage
from scipy import misc
from skimage import filters
from skimage import feature
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from collections import namedtuple
import logging
import numpy
import time
import serial
# create word drawing type, andrews letters and pixel letters
# be able to specify which marker color for letters and for line drawings
# largest size is 450

app = Flask(__name__)






#########################
# SERVO INFO
#########################

# servo 1
# black

# servo2
# red

# servo3
# green

# servo4
# blue






#########################
# IMAGE PROCESSING
#########################

bit_mask_index_3 = 0xF000
bit_mask_index_2 = 0x0F00
bit_mask_index_1 = 0x00F0
bit_mask_index_0 = 0x000F

loc = namedtuple("loc", "x3 x2 x1 x0 y3 y2 y1 y0 servo_num")
locations = []

# only prints black/white
def print_pixels(img, height, width):
  for row in range(1,height):
    for col in range(1,width):
      if (img[row][col][0] == 0):
        print " ",
      else:
        print "X",
    print " "
  return

# canny edge detection
# for line drawing
def canny(img, width):
  img = misc.imresize(img, 300.0/width)
  return feature.canny(img, sigma=3)

def sobel(img):
  img_sx = ndimage.sobel(img, axis=0, mode='constant')
  img_sy = ndimage.sobel(img, axis=1, mode='constant')
  img_mag = numpy.hypot(img_sx, img_sy)
  img_mag *= 255 / numpy.max(img_mag)
  img_resize = misc.imresize(img_mag, 0.25)
  return img_resize

# if r is largest, use red marker
# if g is largest, use green marker
# if b is largest, use blue marker
# if its a grayscale color...
# less than half of 256, use white, aka no marker
# greater than half of 256, use black
def find_closest(r, g, b):
  if (r > g and r > b):
    return 2 # red
  if (g > r and g > b):
    return 3 # green
  if (b > r and b > g):
    return 4 # blue
  if (r == g and r == b):
    if (r < 128):
      return 0 # white, nothing
    else:
      return 1 # black

# create file of points
# for debugging
def create_file_of_points(img, filename):
  text_file = open(filename, "w")
  global locations
  for i in locations:
    to_write =  str(i.x3) + " " + \
                str(i.x2) + " " + \
                str(i.x1) + " " + \
                str(i.x0) + " " + \
                str(i.y3) + " " + \
                str(i.y2) + " " + \
                str(i.y1) + " " + \
                str(i.y0) + " " + \
                str(i.servo_num)
    text_file.write("%s" % to_write)
  text_file.close()
  return

# create array of points
# to send over serial connection
# line drawing, same marker whole time
def create_array_of_points_line(img, height, width, servo_num):
  global locations
  for r in range(0, height):
    for c in range(0, width):
      if (img[r][c] == True):
        c3 = c & bit_mask_index_3
        c2 = c & bit_mask_index_2
        c1 = c & bit_mask_index_1
        c0 = c & bit_mask_index_0
        r3 = r & bit_mask_index_3
        r2 = r & bit_mask_index_2
        r1 = r & bit_mask_index_1
        r0 = r & bit_mask_index_0
        l = loc(str(c3), str(c2), str(c1), str(c0), \
                str(r3), str(r2), str(r1), str(r0), \
                str(servo_num))
        locations.append(l)
  return

def sort():
  # sort the locations array
  # black first
  # red second
  # green third
  # blue last
  black = []
  red = []
  green = []
  blue = []
  new_locations = []
  for i in locations:
    if (i.servo_num == 1):
      black.append(i)
    elif (i.servo_num == 2):
      red.append(i)
    elif (i.servo_num == 3):
      green.append(i)
    elif (i.servo_num == 4):
      blue.append(i)
    while (black):
      add = black.pop(0)
      new_locations.append(add)
    while (red):
      add = red.pop(0)
      new_locations.append(add)
    while (green):
      add = blue.pop(0)
      new_locations.append(add)
    while (blue):
      add = blue.pop(0)
      new_locations.append(add)
  return new_locations

# create array of points
# to send over serial connection
# dot drawing, different marker depending on color
def create_array_of_points_color(img, height, width):
  for r in range(0, height):
    for c in range(0, width):
      c3 = c & bit_mask_index_3
      c2 = c & bit_mask_index_2
      c1 = c & bit_mask_index_1
      c0 = c & bit_mask_index_0
      r3 = r & bit_mask_index_3
      r2 = r & bit_mask_index_2
      r1 = r & bit_mask_index_1
      r0 = r & bit_mask_index_0
      servo_num = find_closest(img[r][c][0], img[r][c][1], img[r][c][0])
      if (servo_num != 0):
        l = loc(str(c3), str(c2), str(c1), str(c0), \
                str(r3), str(r2), str(r1), str(r0), \
                str(servo_num))
        locations.append(l)
  return

def create_array_of_alpha():
  return

def resize(img, height, width):
  if (width > 450):
    img = misc.imresize(img, 450.0/width)
    height = len(img[:][:][:])
  if (height > 450):
    img = misc.imresize(img, 450.0/height)
  return img





#########################
# SERIAL
#########################

ser = 0

def test_90_loop():
  start = time.time()
  x = 0
  for i in range(0,90000):
    x += 1
  end = time.time()
  print (end - start)
  return


def init_serial():
  global ser
  ser = serial.Serial(
               port = '/dev/tty.SLAB_USBtoUART',
               baudrate= 57600,
               parity= serial.PARITY_NONE,
               stopbits= serial.STOPBITS_ONE,
               bytesize= serial.EIGHTBITS
               )
  return

def send_file(filename):
  global ser
  readline = lambda : iter(lambda:ser.read(1),"\n")
  while "".join(readline()) != "<<send>>":
    # waiting for client to request file
    pass
  ser.write(open(filename, "rb").read())
  ser.write("\n<<end>>\n")
  return

def send_points():
  global locations
  global ser
  readline = lambda : iter(lambda:ser.read(1),"\n")
  while "".join(readline()) != "<<send>>":
    # waiting
    pass
  for i in locations:
    ser.write(str(i.x3))
    ser.write(str(i.x2))
    ser.write(str(i.x1))
    ser.write(str(i.x0))
    ser.write(str(i.y3))
    ser.write(str(i.y2))
    ser.write(str(i.y1))
    ser.write(str(i.y0))
    ser.write(str("0"))
    ser.write(str("0"))
    ser.write(str("0"))
    ser.write(str(i.servo_num))
    while "".join(readline()) != "<<send>>":
      # waiting
      pass
  ser.write("\n<<end>>\n")
  return

def test_serial():
  init_serial()
  return



#########################
# DRAWING MODES
#########################


def type1(img, height, width):
  # line drawing
  init_serial()
  new_img = canny(img, width)
  create_array_of_points_line(new_img, height, width, 1) # always black line
  send_points()
  return


def type2(img, height, width):
  # dot drawing
  init_serial()
  new_img = resize(img)
  create_array_of_points_color(new_img, height, width)
  locations = sort()
  send_points()
  return

def type3(words):
  # word drawing
  init_serial()
  create_array_of_alpha()
  return






#########################
# FLASK UPLOADING IMAGE FROM SERVER
#########################

@app.route('/type1', methods=['GET', 'POST'])
# line drawing
def type1_start():
  image = request.files.get('image-file', '')
  img = ndimage.imread(image)
  height = len(img[:][:][:])
  width = len(img[0][:][:])
  type1(img, height, width)
  return "done"

@app.route('/type2', methods=['GET', 'POST'])
def type2_start():
  image = request.files.get('image-file', '')
  img = ndimage.imread(image)
  height = len(img[:][:][:])
  width = len(img[0][:][:])
  type2(img, height, width)
  return "done"

@app.route('/type3', methods=['GET', 'POST'])
def type3_start():
  words = request.args['data']
  type3(words)
  return "done"




#########################
# HTML TEMPLATE STUFF
#########################

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

# change this later
@app.route('/favicon.ico')
def favicon():
  return send_from_directory('Documents/EECS373/final_proj/images', 'test.png')

if __name__ == '__main__':
  test_serial()


