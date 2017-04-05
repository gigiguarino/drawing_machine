//
//  final_proj.cpp
//  Created by Gabrielle Guarino on 4/1/17.

#include <iostream>
#include <cmath>
#include <vector>
#include "CImg-2.0.0_pre032917/CImg.h"
using namespace std;

// CImg?

// when placing dots:
// start at lowest row
// left to right
// go to next row
// right to left
// etc

struct color {
  int r;
  int g;
  int b;
};

struct pixel_loc {
  int x;
  int y;
};

int num_colors = 4;
color colors[4];
vector < vector<pixel_loc> > locations;

bool row_sort (pixel_loc a, pixel_loc b)
{
  return a.x < b.x;
}

bool col_sort1 (pixel_loc a, pixel_loc b)
{
  return a.y > b.y;
}

bool col_sort2 (pixel_loc a, pixel_loc b)
{
  return a.y < b.y;
}

int find_closest(color color_in)
{
  // matches color to closest marker color
  // and returns which vector_num it matches
  
  float diff, current_diff;
  diff = 10000;
  
  int vector_num;
  
  int r1 = color_in.r;
  int g1 = color_in.g;
  int b1 = color_in.b;
  int r2, g2, b2;
  
  for (int i = 0; i < num_colors; i++)
  {
    r2 = colors[i].r;
    g2 = colors[i].g;
    b2 = colors[i].b;
    
    current_diff = sqrt(pow((r2 - r1), 2) + pow((g2 - g1), 2) + pow((b2 - b1), 2));
    
    if (current_diff < diff)
    {
      diff = current_diff;
      vector_num = i;
    }
  }

  return vector_num;
}

void sort_vector(int num) {
  
  // first sort it by rows
  sort(locations[num].begin(), locations[num].end(), row_sort);
  
  int current_row = locations[num][0].x;
  bool sort1 = true;
  
  int start_num = 0;
  int end_num = 0;
  
  for (int i = 0; i < locations[num].size(); i++)
  {
    end_num = i - 1;
    
    if (locations[num][i].x != current_row && sort1)
    {
      sort (locations[num].begin()+start_num, locations[num].begin()+end_num, col_sort1);
      current_row = locations[num][i].x;
      start_num = i;
      sort1 = false;
    }
    
    else if (locations[num][i].x != current_row && !sort1)
    {
      sort (locations[num].begin()+start_num, locations[num].begin()+end_num, col_sort2);
      current_row = locations[num][i].x;
      start_num = i;
      sort1 = true;
    }
  }
}

void process_image(cimg_library::CImg<unsigned char> img) {
  int width = img.width();
  int height = img.height();
  
  int current_num;
  color current_color;
  pixel_loc current_loc;
  
  for (int row = 0; row < width; row++)
  {
    for (int col = 0; col < height; col++)
    {
      current_color.r = (int)img(row, col, 0, 0);
      current_color.g = (int)img(row, col, 0, 1);
      current_color.b = (int)img(row, col, 0, 2);
      
      current_num = find_closest(current_color);
      
      current_loc.x = row;
      current_loc.y = col;
      
      locations[current_num].push_back(current_loc);
    }
  }
}

void color_init ()
{
  for (int i = 0; i < num_colors; i++)
  {
    colors[i].r = 256;
    colors[i].g = 256;
    colors[i].b = 256;
  }
}

int main(void)
{
  color_init();
  
  cimg_library::CImg<unsigned char> img("test.png");
  int width = img.width();
  int height = img.height();
  
  // start by resizing image considerably so we have less pixels
  // to go through
  
  // 8.5*20 = 170
  // 11*20 = 220
  
  
  float ratio = width/height;
  // if ratio is greater than 1, width is larger
  // if ratio is less than 1, width is smaller
  
  int new_height = 0;
  int new_width = 0;
  
  if (ratio < 1) {
    // resize to width 850 pixels
    new_width = 170;
    new_height = new_width/ratio;
    img.resize(new_width, new_height, 1, 3, 1, 0, 0, 0, 0, 0);
    
  } else {
    // resize to height 1100 pixels
    new_height = 220;
    new_width = new_height * ratio;
    img.resize(new_width, new_height, 1, 3, 1, 0, 0, 0, 0, 0);
  }

  
  
  return 0;
}
