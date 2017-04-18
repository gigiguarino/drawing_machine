#!/usr/bin/env python
from sklearn.neighbors import NearestNeighbors
from scipy import ndimage
from scipy import misc
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from collections import namedtuple
import networkx as nx
import numpy as np
import serial
import math
import sys

# create word drawing type, andrews letters and pixel letters
# be able to specify which marker color for letters and for line drawings
# largest size is 450

app = Flask(__name__, static_folder='static', static_url_path='/static')


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


# parameter passed in for this one
def print_locations(locs):
  sys.stdout.write("locations:\n")
  sys.stdout.write("\n")
  for l in locs:
    sys.stdout.write("x: " + str(l.x3) + str(l.x2) + str(l.x1) + str(l.x0) + "\n")
    sys.stdout.write("y: " + str(l.y3) + str(l.y2) + str(l.y1) + str(l.y0) + "\n")
    sys.stdout.write("servo: " + str(l.servo_num) + "\n")
    sys.stdout.write("\n")
  sys.stdout.flush()

# prints a single location
# for when sending serial
# to debug in terminal
def print_location(l):
  sys.stdout.write("[" + str(l.x3) + str(l.x2) + str(l.x1) + str(l.x0) \
    + "," + str(l.y3) + str(l.y2) + str(l.y1) + str(l.y0) + "]")
  sys.stdout.flush()

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

# gets string value of the number
def get_string4(num):
  str1 = str(num/1000)
  num = num % 1000
  str2 = str(num/100)
  num = num % 100
  str3 = str(num/10)
  num = num % 10
  str4 = str(num)
  string = str1 + str2 + str3 + str4
  return string


# makes a points array from the data string
def get_points(data, servo_num):
  lines = data.splitlines()
  points = []
  for line in lines:
    point = []
    vars = line.split()
    if (vars[2] == str(servo_num)):
      point.append(vars[0])
      point.append(vars[1])
      points.append(point)
  return points


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

# returns 1 if its a jump
def is_jump(x0, y0, x1, y1):
  x0 = int(x0)
  y0 = int(y0)
  x1 = int(x1)
  y1 = int(y1)
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


# removes the indices specified
def remove_locs(locs, this_locations):
  for l in locs:
    for t in this_locations:
      if (l == t):
        this_locations.remove(t);
        break
  return this_locations

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
      loc1.y3 == loc2.y3 and loc1.y2 == loc2.y2 and loc1.y1 == loc2.y1 and loc1.y0 == loc2.y0):
    return 1
  else:
    return 0



# adds the dot jump locations to the array
# if the dot locations are vertically in line with eachother
# then they are a vertical line
def add_dot_jumps(dot_locations, this_locations):
  for d in dot_locations:
    d = loc(d.x3, d.x2, d.x1, d.x0, d.y3, d.y2, d.y1, d.y0, 0)
    for l in this_locations:
      if (equal_x_y(d, l)):
        this_locations.insert(this_locations.index(l), d)
        break
  return this_locations



# add jump discontinuities where move the servo up
# for line segments
def add_jumps(this_locations):
  dots_to_add = []
  prev_x = -1
  prev_y = -1
  for i in range(0, len(this_locations)):
    curr_x = convert_to_x(this_locations[i])
    curr_y = convert_to_y(this_locations[i])
    if (prev_x < 0 and prev_y < 0):
      dots_to_add.append(this_locations[i])
    else:
      # not on first location anymore
      if (is_jump(prev_x, prev_y, curr_x, curr_y)):
        dots_to_add.append(this_locations[i])
    prev_x = curr_x
    prev_y = curr_y
  this_locations = add_dot_jumps(dots_to_add, this_locations)
  return this_locations

# returns true if its a connected straight line
def is_line(curr_x, curr_y, next_x, next_y, prev_x, prev_y):
  if (curr_x == next_x and curr_x == prev_x):
    if (next_y == curr_y + 1 and prev_y == curr_y - 1):
      return 1
    if (next_y == curr_y - 1 and prev_y == curr_y + 1):
      return 1
    else:
      return 0
  if (curr_y == next_y and curr_y == prev_y):
    if (next_x == curr_x + 1 and prev_x == curr_x - 1):
      return 1
    if (next_x == curr_x - 1 and prev_x == curr_x + 1):
      return 1
    else:
      return 0
  else:
    return 0

# returns true if its a connected straight diagonal
def is_diagonal(curr_x, curr_y, next_x, next_y, prev_x, prev_y):
  if (curr_x == prev_x + 1 and curr_x == next_x - 1):
    if (curr_y == prev_y - 1 and curr_y == next_y + 1):
      return 1
    if (curr_y == prev_y + 1 and curr_y == next_y - 1):
      return 1
    else:
      return 0
  if (curr_x == prev_x - 1 and curr_x == next_x + 1):
    if (curr_y == prev_y - 1 and curr_y == next_y + 1):
      return 1
    if (curr_y == prev_y + 1 and curr_y == next_y - 1):
      return 1
    else:
      return 0
  else:
    return 0

# removes lines and diagonals so they use less movements
def remove_unnecessary_moves(this_locations):
  prev_servo = 0
  prev_x = 0
  prev_y = 0
  to_remove = []
  for i in range(0, len(this_locations) - 1):
    curr_x = convert_to_x(this_locations[i])
    curr_y = convert_to_y(this_locations[i])
    curr_servo = this_locations[i].servo_num
    next_x = convert_to_x(this_locations[i+1])
    next_y = convert_to_y(this_locations[i+1])
    next_servo = this_locations[i+1].servo_num
    if (curr_servo != 0 and next_servo != 0 and prev_servo != 0):
      if (is_diagonal(curr_x, curr_y, next_x, next_y, prev_x, prev_y) or
          is_line(curr_x, curr_y, next_x, next_y, prev_x, prev_y)):
        # remove i from this_locations
        to_remove.append(this_locations[i])
    prev_x = curr_x
    prev_y = curr_y
    prev_servo = curr_servo
  this_locations = remove_locs(to_remove, this_locations)
  return this_locations


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
def create_array_of_points_line(plot_points, height, width, servo_num):
  this_locations = []
  # nearest neighbor calculation
  x_array = get_x(plot_points)
  y_array = get_y(plot_points)
  lines = nearest_neighbor(x_array, y_array)
  if (len(lines) > 1):
    points = make_one_array(lines)
  else:
    points = lines[0]
  points = plot_points  #######################
  # add to locations list
  for l in range(0, len(points)):
    x = int(points[l][0])
    y = int(points[l][1])
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
    this_locations.append(l1)
  return this_locations

# since i pass in a 100x100 drawing
# i want to output a 200x200 drawing because it's larger
# and our x-y positioning is very precise and small
def make_locations_bigger():
  global locations
  for i in range(0, len(locations)):
    x_str = get_string4(2*convert_to_x(locations[i]))
    y_str = get_string4(2*convert_to_y(locations[i]))
    locations[i] = loc(x_str[0], x_str[1], x_str[2], x_str[3], \
      y_str[0], y_str[1], y_str[2], y_str[3], locations[i].servo_num)
  return


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
    sys.stdout.write("recieved ack " + str(num) + "...")
    sys.stdout.flush()
    num += 1
  sys.stdout.write("done sending locations...")
  sys.stdout.flush()
  return

# splits up locations into smaller
# lists to send over serial connection
def split_locations():
  global locations
  make_servo_zero(locations[0])
  new_locations = []
  for i in range(0, 500):
    new_locations.append(locations[i])
  for i in range(0, 499):
    locations.pop(0)
  return new_locations


def combine_locations(black, red, green, blue):
  global locations
  locations = []
  for a in black:
    locations.append(a)
  for b in red:
    locations.append(b)
  for c in green:
    locations.append(c)
  for d in blue:
    locations.append(d)
  return

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


#########################
# DRAWING INIT
#########################


def draw(data_string, height, width):
  # line drawing
  black_points = get_points(data_string, 1)
  red_points = get_points(data_string, 2)
  green_points = get_points(data_string, 3)
  blue_points = get_points(data_string, 4)
  black_loc = []
  red_loc = []
  green_loc = []
  blue_loc = []
  if (len(black_points) > 0):
    black_loc = create_array_of_points_line(black_points, height, width, 1)
    black_loc = add_jumps(black_loc)
    black_loc = remove_unnecessary_moves(black_loc)
  if (len(red_points) > 0):
    red_loc = create_array_of_points_line(red_points, height, width, 2)
    red_loc = add_jumps(red_loc)
    red_loc = remove_unnecessary_moves(red_loc)
  if (len(green_points) > 0):
    green_loc = create_array_of_points_line(green_points, height, width, 3)
    green_loc = add_jumps(green_loc)
    green_loc = remove_unnecessary_moves(green_loc)
  if (len(blue_points) > 0):
    blue_loc = create_array_of_points_line(blue_points, height, width, 4)
    blue_loc = add_jumps(blue_loc)
    blue_loc = remove_unnecessary_moves(blue_loc)
  combine_locations(black_loc, red_loc, green_loc, blue_loc)
  print_locations(locations)
  sys.stdout.write("starting serial...")
  sys.stdout.flush()
  init_serial()
  while (len(locations) > 500):
    curr_loc = split_locations()
    send_points(curr_loc)
  send_points(locations)
  return


def image_test(height, width):
  img = np.zeros((height, width, 3), dtype=np.uint8)
  for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        if (y == 10 and x == 20):
          img[y][x][0] = 255;
          img[y][x][1] = 255;
          img[y][x][2] = 255;
        elif (y == 20 and x == 10):
          img[y][x][0] = 255;
          img[y][x][1] = 0;
          img[y][x][2] = 0;
        else:
          img[y][x][0] = 0;
          img[y][x][0] = 0;
          img[y][x][0] = 0;
  misc.imsave("test.png", img);


def create_image(data, height, width):
  img = np.zeros((height, width, 3), dtype=np.uint8)
  for y in range(img.shape[0]):
    for x in range(img.shape[1]):
      img[y][x][0] = 255;
      img[y][x][1] = 255;
      img[y][x][2] = 255;
  lines = data.splitlines()
  for line in lines:
    current_points = line.split()
    current_x = int(current_points[0])
    current_y = int(current_points[1])
    current_servo = int(current_points[2])
    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        if (y == current_y and x == current_x):
            if (current_servo == 1):
              img[y][x][0] = 0;
              img[y][x][1] = 0;
              img[y][x][2] = 0;
            if (current_servo == 2):
              img[y][x][0] = 255;
              img[y][x][1] = 0;
              img[y][x][2] = 0;
            if (current_servo == 3):
              img[y][x][0] = 0;
              img[y][x][1] = 255;
              img[y][x][2] = 0;
            if (current_servo == 4):
              img[y][x][0] = 0;
              img[y][x][1] = 0;
              img[y][x][2] = 255;
  return img


def get_new_data(img):
  new_data = ""
  for y in range(img.shape[0]):
    for x in range(img.shape[1]):
      if (not(img[y][x][0] == 255 and img[y][x][1] == 255 and img[y][x][2] == 255)):
        if (img[y][x][0] == img[y][x][1] and img[y][x][1] == img[y][x][2]):
          new_data += str(x) + " " + str(y) + " " + str(1) + "\n"
        elif (img[y][x][1] < img[y][x][0] and img[y][x][2] < img[y][x][0]):
          new_data += str(x) + " " + str(y) + " " + str(2) + "\n"
        elif (img[y][x][0] < img[y][x][1] and img[y][x][2] < img[y][x][1]):
          new_data += str(x) + " " + str(y) + " " + str(3) + "\n"
        elif (img[y][x][0] < img[y][x][2] and img[y][x][1] < img[y][x][2]):
          new_data += str(x) + " " + str(y) + " " + str(4) + "\n"
  return new_data



#########################
# FLASK UPLOADING IMAGE FROM SERVER
#########################

@app.route('/start', methods=['GET', 'POST'])
def start():
  # read from file called points.txt
  # to get the points and different colors
  sys.stdout.write("inside python...")
  sys.stdout.flush()
  data = request.get_data()
  img = create_image(data, 100, 100)
  img = misc.imresize(img, 200, 'nearest')
  misc.imsave("resized_img.png", img)
  data = get_new_data(img)
  sys.stdout.write("starting image processing...")
  sys.stdout.flush()
  draw(data, 200, 200)
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
  return send_from_directory('Documents/EECS373/drawing_machine/images', 'favicon.ico')

if __name__ == '__main__':
  app.run(debug=True)


