#!/usr/bin/env python
from scipy import ndimage
from scipy import misc
from skimage import filters
from skimage import feature
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from serial import Serial
from collections import namedtuple
import logging
import numpy


app = Flask(__name__)


#########################
# SERIAL
#########################

ser = 0

def init_serial():
  global ser
  ser = Serial(
    port = '/dev/ttys000',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
  )

def send_file(filename):
  global ser
  readline = lambda : iter(lambda:ser.read(1),"\n")
  while "".join(readline()) != "<<send>>":
     # waiting for client to request file
     pass
  ser.write(open(filename, "rb").read())
  ser.write("\n<<end>>\n")

def send_points():
  global locations
  global ser
  readline = lambda : iter(lambda:ser.read(1),"\n")
  while "".join(readline()) != "<<send>>":
    # waiting
    pass
  for x in locations:
    ser.write(str(x.x))
    ser.write(str(x.y))
  ser.write("\n<<end>>\n")


#########################
# IMAGE PROCESSING
#########################
loc = namedtuple("loc", "x y")
locations = []

def print_pixels(img):
  height = len(img[:][:][:])
  width = len(img[0][:][:])
  for row in range(1,height):
    for col in range(1,width):
      if (img[row][col][0] == 0):
        print " ",
      else:
        print "X",
    print " "

def canny(img):
  width = len(img[0][:])
  img = misc.imresize(img, 300.0/width)
  return feature.canny(img, sigma=3)


def sobel(img):
  img_sx = ndimage.sobel(img, axis=0, mode='constant')
  img_sy = ndimage.sobel(img, axis=1, mode='constant')
  img_mag = numpy.hypot(img_sx, img_sy)
  img_mag *= 255 / numpy.max(img_mag)
  img_resize = misc.imresize(img_mag, 0.25)
  return img_resize


def create_file_of_points(img, filename):
  text_file = open(filename, "w")
  global locations
  for x in locations:
    to_write = str(x.x) + " " + str(x.y) + "\n"
    text_file.write("%s" % to_write)
  text_file.close()

def create_array_of_points(img):
  global locations
  width = len(img[0][:])
  height = len(img[:][:])
  for r in range(0, height):
    for c in range(0, width):
      if (img[r][c] == True):
        l = loc(str(c), str(r))
        locations.append(l)




def edge_detection_test():
  image1 = ndimage.imread('images/test1.jpg', mode="RGB")
  image2 = ndimage.imread('images/test2.jpg', mode="RGB")
  image3 = ndimage.imread('images/test3.jpg', mode="RGB")
  image4 = ndimage.imread('images/test4.jpg', mode="RGB")
  
  image1_grey = numpy.dot(image1[...,:3],[0.3, 0.6, 0.1])
  image2_grey = numpy.dot(image2[...,:3],[0.3, 0.6, 0.1])
  image3_grey = numpy.dot(image3[...,:3],[0.3, 0.6, 0.1])
  image4_grey = numpy.dot(image4[...,:3],[0.3, 0.6, 0.1])

  image1_c_r = canny(image1_grey)
  image2_c_r = canny(image2_grey)
  image3_c_r = canny(image3_grey)
  image4_c_r = canny(image4_grey)
  
  create_file_of_points(image1_c_r, "output1.txt")
  create_file_of_points(image1_c_r, "output2.txt")
  create_file_of_points(image1_c_r, "output3.txt")
  create_file_of_points(image1_c_r, "output4.txt")

  misc.imsave('output_images/test1_canny.jpg', image1_c_r)
  misc.imsave('output_images/test2_canny.jpg', image2_c_r)
  misc.imsave('output_images/test3_canny.jpg', image3_c_r)
  misc.imsave('output_images/test4_canny.jpg', image4_c_r)




#########################
# FLASK UPLOADING IMAGE FROM SERVER
#########################

@app.route('/upload', methods=['GET', 'POST'])
def start():
  image = request.files.get('image-file', '')
  img = ndimage.imread(image)
  height = len(img[:][:][:])
  width = len(img[0][:][:])
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
  #app.run(debug=True)
  edge_detection_test()
