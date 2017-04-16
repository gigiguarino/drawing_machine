#!/usr/bin/env python
from sklearn.neighbors import NearestNeighbors
from scipy import ndimage
from scipy import misc
from skimage import filters
from skimage import feature
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from collections import namedtuple
import networkx as nx
import numpy as np
import serial
import math

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

# useful for debugging purposes
# prints whole locations array
def print_locations():
  print "locations:"
  print " "
  for l in locations:
    print "x: " + str(l.x3) + str(l.x2) + str(l.x1) + str(l.x0)
    print "y: " + str(l.y3) + str(l.y2) + str(l.y1) + str(l.y0)
    print "servo: " + str(l.servo_num)
    print " "

# prints a single location
# for when sending serial
# to debug in terminal
def print_location(l):
  print "[" + str(l.x3) + str(l.x2) + str(l.x1) + str(l.x0) \
    + "," + str(l.y3) + str(l.y2) + str(l.y1) + str(l.y0) + "]"

# takes in a location and outputs the number
# that corresponds to the x value strings
def convert_to_x(l):
  num_str = l.x3 + l.x2 + l.x1 + l.x0
  return int(num_str)

# takes in a location and outputs the number that
# corresponds to the y value strings
def convert_to_y(l):
  num_str = l.y3 + l.y2 + l.y1 + l.y0
  return int(num_str)

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

# whack
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

# create an array of points in the image that
# are black
def get_plot_points(img, height, width):
  plot_points = []
  for c in range(0, width):
    for r in range(0, height):
      if (img[r][c][1] == 0):
        point = []
        point.append(c)
        point.append(r)
        plot_points.append(point[:])
        del point[:]
  return plot_points

# returns x values of the points in the array
def get_x(points):
  new_array = []
  for i in range(0, len(points)):
    new_array.append(points[i][0])
  return new_array

# returns y values of the points in the array
def get_y(points):
  new_array = []
  for i in range(0, len(points)):
    new_array.append(points[i][1])
  return new_array

# reorders the nodes returned from nearest neighbor
# into an actual able-to-plot array
def reorder(points, order, x):
  new_array = []
  for z in range(0, len(order)):
    if (x == 1):
      new_array.append(points[order[z]][0])
    else:
      new_array.append(points[order[z]][1])
  return new_array

# removes the points that have been added as a line
def remove_new(new_points, points):
  for i in new_points:
    num = 0
    for j in points:
      if (i[0] == j[0] and i[1] == j[1]):
        points = np.delete(points, num, 0)
      num += 1
  return points



# returns a number corresponding to which type of diagonal
# 0 if no diagonal
# 1 if up and left, y decreases, x decreases
# 2 if up and right, y decreases, x increases
# 3 if down and left, y increases, x decreases
# 4 if down and right, y increases, x increases
def diagonal(x0, y0, x1, y1):
  x0 = int(x0)
  x1 = int(x1)
  y0 = int(y0)
  y1 = int(y1)
  if (((x0 - x1) == (y0 - y1)) and ((x0 - x1) > 0)):
    return "1"
  elif (((x0 - x1) == (y0 - y1)) and ((x0 - x1) < 0)):
    return "4"
  elif (((x0 - x1) == (-1)*(y0 - y1)) and ((x0 - x1) < 0)):
    return "2"
  elif (((x0 - x1) == (-1)*(y0 - y1)) and ((x0 - x1) > 0)):
    return "3"
  else:
    return "0"

# checks if these points for a line
def check_line(x0, y0, x1, y1):
  x0 = int(x0)
  y0 = int(y0)
  x1 = int(x1)
  y1 = int(y1)
  if (x0 == x1):
    return "x"
  elif (y0 == y1):
    return "y"
  elif (diagonal(x0, y0, x1, y1) != "0"):
    return "d" + diagonal(x0, y0, x1, y1)
  else:
    return "0"

def is_jump(x0, y0, x1, y1):
  if (((x0 - x1) == (y0 - y1)) and ((x0 - x1) > 0)):
    return 0
  elif (((x0 - x1) == (y0 - y1)) and ((x0 - x1) < 0)):
    return 0
  elif (((x0 - x1) == (-1)*(y0 - y1)) and ((x0 - x1) < 0)):
    return 0
  elif (((x0 - x1) == (-1)*(y0 - y1)) and ((x0 - x1) > 0)):
    return 0
  elif (x0 == x1 and y0 == y1 + 1):
    return 0
  elif (x0 == x1 and y1 == y0 + 1):
    return 0
  elif (y0 == y1 and x0 == x1 + 1):
    return 0
  elif (y0 == y1 and x1 == x0 + 1):
    return 0
  else:
    return 1

# for jumps the servo needs to move up
def make_servo_zero(l):
  global locations
  for i in range(0, len(locations)):
    if (l == locations[i]):
      locations[i] = loc(l.x3, l.x2, l.x1, l.x0, l.y3, l.y2, l.y1, l.y0, 0)
      break
  return

# for end connection the servo needs to move down
def make_servo_one(l):
  global locations
  for i in range(0, len(locations)):
    if (l == locations[i]):
      locations[i] = loc(l.x3, l.x2, l.x1, l.x0, l.y3, l.y2, l.y1, l.y0, 1)
  return

# tells if two locations are equal
# their servo num doesn't matter
def equal_x_y(loc1, loc2):
  if (loc1.x3 == loc2.x3 and loc1.x2 == loc2.x2 and loc1.x1 == loc2.x1 and loc1.x0 == loc2.x0 and
      loc1.y3 == loc2.y3 and loc1.y2 == loc2.y2 and loc1.y1 == loc2.y1 and loc1.y0 and loc2.y0):
    return 1
  else:
    return 0

def add_dot_jumps(dot_locations):
  global locations
  for d in dot_locations:
    for l in locations:
      if (equal_x_y(d, l)):
        locations.insert(locations.index(l)+1, d)
        break
  return

# add jump discontinuities where move the servo up
# for line segments
def add_jumps():
  global locations
  dots_to_add = []
  prev_x = -1
  prev_y = -1
  for i in locations:
    curr_x = convert_to_x(i)
    curr_y = convert_to_y(i)
    line = "0"
    jump = 1
    if (prev_x < 0 and prev_y < 0):
      make_servo_zero(i)
      dots_to_add.append(i)
    else:
      # not on first location anymore
      jump = is_jump(prev_x, prev_y, curr_x, curr_y);
      if (is_jump(prev_x, prev_y, curr_x, curr_y)):
        if (prev_jump and jump):
          # dot
          dots_to_add.append(i)
        # move servo up
        make_servo_zero(i)
      elif ((check_line(prev_x, prev_y, curr_x, curr_y) == prev_line) and (prev_line != "0")):
        # this is a straight line
        # previous location can be removed
        line = check_line(prev_x, prev_y, curr_x, curr_y)
        locations.remove(prev_l)
    prev_x = curr_x
    prev_y = curr_y
    prev_l = i
    prev_line = line
    prev_jump = jump
  add_dot_jumps(dots_to_add)
  return

# concatenates the lines into one array
def make_one_array(lines):
  points = []
  for line in lines:
    for x in line:
      points.append(x)
  return points



# finds the nearest neighbors of the points in plot points
# returns the new array of points, ordered by their neighbors
def nearest_neighbor(x, y):
  points = np.c_[x,y]
  if (len(points) <= 2):
    return points
  new_x = x
  new_y = y
  lines = []
  while (len(points) != 0):
    clf = NearestNeighbors(2).fit(points)
    G = clf.kneighbors_graph()
    T = nx.from_scipy_sparse_matrix(G)
    order = list(nx.dfs_preorder_nodes(T,0))
    new_x = reorder(points, order, 1)
    new_y = reorder(points, order, 0)
    new_points = np.c_[new_x, new_y]
    if ((is_jump(new_points[len(new_points)-1][0], new_points[len(new_points)-1][1],
           new_points[0][0], new_points[0][1]) == 0)):
      new_points = np.vstack([new_points, new_points[0]])
    lines.append(new_points)
    points = remove_new(new_points, points)
  return lines



# create array of points
# to send over serial connection
# line drawing, same marker whole time
def create_array_of_points_line(img, height, width, servo_num):
  global locations
  plot_points = get_plot_points(img, height, width)
  x_array = get_x(plot_points)
  y_array = get_y(plot_points)
  # nearest neighbor calculation
  lines = nearest_neighbor(x_array, y_array)
  points = make_one_array(lines)
  for l in range(0, len(points)):
    x = points[l][0]
    y = points[l][1]
    if (x >= 100):
      x3 = str(0)
      x2 = str(x)[0]
      x1 = str(x)[1]
      x0 = str(x)[2]
    elif (x >= 10):
      x3 = str(0)
      x2 = str(0)
      x1 = str(x)[0]
      x0 = str(x)[1]
    else:
      x3 = str(0)
      x2 = str(0)
      x1 = str(0)
      x0 = str(x)
    if (y >= 100):
      y3 = str(0)
      y2 = str(y)[0]
      y1 = str(y)[1]
      y0 = str(y)[2]
    elif (y >= 10):
      y3 = str(0)
      y2 = str(0)
      y1 = str(y)[0]
      y0 = str(y)[1]
    else:
      y3 = str(0)
      y2 = str(0)
      y1 = str(0)
      y0 = str(y)
    l1 = loc(str(x3), str(x2), str(x1), str(x0), \
             str(y3), str(y2), str(y1), str(y0), \
             str(servo_num))
    locations.append(l1)
  return


# sort the locations array
# black first
# red second
# green third
# blue last
def sort():
  global locations
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
  global locations
  for r in range(0, height):
    for c in range(0, width):
      if (r >= 100):
        r3 = str(0)
        r2 = str(r)[0]
        r1 = str(r)[1]
        r0 = str(r)[2]
      elif (r >= 10):
        r3 = str(0)
        r2 = str(0)
        r1 = str(r)[0]
        r0 = str(r)[1]
      else:
        r3 = str(0)
        r2 = str(0)
        r1 = str(0)
        r0 = str(r)
      if (c >= 100):
        c3 = str(0)
        c2 = str(c)[0]
        c1 = str(c)[1]
        c0 = str(c)[2]
      elif (c >= 10):
        c3 = str(0)
        c2 = str(0)
        c1 = str(c)[0]
        c0 = str(c)[1]
      else:
        c3 = str(0)
        c2 = str(0)
        c1 = str(0)
        c0 = str(c)
      servo_num = find_closest(img[r][c][0], img[r][c][1], img[r][c][2])
      if (servo_num != 0):
        l = loc(str(c3), str(c2), str(c1), str(c0), \
                str(r3), str(r2), str(r1), str(r0), \
                str(servo_num))
        locations.append(l)
  return

def resize(img, height, width):
  if (width > 450):
    img = misc.imresize(img, 450.0/width)
    height = len(img[:][:][:])
  if (height > 450):
    img = misc.imresize(img, 450.0/height)
  return img

def create_array_of_alpha(words):
  for i in words:
    points = []
    if (i == " "):
      add_space()
    else:
      get_points(words[i])



#########################
# SERIAL
#########################

ser = 0

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
  ser.write("<<end>>")
  return

def send_points(locs):
  global ser
  num_points = len(locs)
  num = 0
  ser.write(str(1))
  ser.read(1)
  # get num to write
  to_write = ""
  if (num_points >= 1000):
    to_write = str(num_points)
  elif (num_points >= 100):
    to_write = str(0) + str(num_points)
  elif (num_points >= 10):
    to_write = str(0) + str(0) + str(num_points)
  else:
    to_write = str(0) + str(0) + str(0) + str(num_points)
  # waiting for read
  ser.write(to_write[0])
  ser.write(to_write[1])
  ser.write(to_write[2])
  ser.write(to_write[3])
  ser.read(1)
  for i in locs:
    ser.write(str(i.x3))
    ser.write(str(i.x2))
    ser.write(str(i.x1))
    ser.write(str(i.x0))
    ser.write(str(i.y3))
    ser.write(str(i.y2))
    ser.write(str(i.y1))
    ser.write(str(i.y0))
    ser.write(str(0))
    ser.write(str(0))
    ser.write(str(0))
    ser.write(str(i.servo_num))
    ser.read(1)
    print "recieved ack " + str(num) + "..."
    num += 1
  print "done sending locations..."
  return

# splits up locations into smaller
# lists to send over serial connection
def split_locations():
  global locations
  make_servo_zero(locations[0])
  if (len(locations) > 500):
    new_locations = []
    for i in range(0, 500):
      new_locations.append(locations[i])
    for i in range(0, 499):
      locations.pop(0)
    return new_locations
  else:
    return locations

# breaks up locations into smaller chunks
# to send to serial
def send_to_serial():
  length = 0
  max_length = len(locations)
  while (length < max_length):
    new_locations = split_locations()
    length = length + len(new_locations)
    send_points(new_locations)
  return

def test1():
  img = ndimage.imread("images/flower.png")
  height = len(img[:][:][:])
  width = len(img[0][:][:])
  create_array_of_points_line(img, height, width, 4)
  add_jumps()
  init_serial()
  send_to_serial()
  return


#########################
# DRAWING MODES
#########################


def type1(img, height, width, servo_num, resize):
  # line drawing
  if (resize):
    new_img = resize(img)
    create_array_of_points_line(new_img, height, width, servo_num)
  else:
    create_array_of_points_line(img, height, width, servo_num)
  add_jumps()
  init_serial()
  send_points()
  return



#########################
# FLASK UPLOADING IMAGE FROM SERVER
#########################

@app.route('/start', methods=['GET', 'POST'])
def start():
  # read from file called points.txt
  # to get the points and different colors
  height = 200
  width = 200
  





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
  test1()


