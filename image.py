#!/usr/bin/env python
from scipy import ndimage
from scipy import misc
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from collections import namedtuple
import logging
import serial


app = Flask(__name__)

location = namedtuple("location", "x y")
locations = []

def send_locations():
  for i in range(1, len(locations)):
    


@app.route('/upload', methods=['GET', 'POST'])
def start():
  image = request.files.get('image-file', '')
  img = ndimage.imread(image)
  height = len(img[:][:][:])
  width = len(img[0][:][:])
  for i in range(1,width):
    for j in range(1,height):
      print_statement = "r: " + str(img[i][j][0]) + "\ng: " + str(img[i][j][1]) + "\nb: " + str(img[i][j][2])
      app.logger.info(print_statement)
  return "done"

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

# change this later
@app.route('/favicon.ico')
def favicon():
  return send_from_directory('Documents/EECS373/final_proj/images', 'test.png')

if __name__ == '__main__':
  app.run(debug=True)
