//
//  image_processing.c
//  

// PImage

// place all colors individually
// reset to 0 position afterward

#include "image_processing.h"

enum sharpie_color { COLOR1, COLOR2, COLOR3, COLOR4 };

PImage image;
string filename;

float points_per_inch = 5;
float paper_height = 11; // inches
float paper_width = 8.5; // inches

float height = paper_height * points_per_inch;
float width = paper_width * points_per_inch;

int num_colors = 4;

color markers[num_colors];

// paper size is
// 8.5 by 11
// 850 pixels by 1100?
// 425 pixels by 550?

struct color {
  sharpie_color sc;
  int red;
  int green;
  int blue;
  int pixels[height][width];
};

void load_image()
{
  image = loadImage(filename);
  // resize image, so less pixels to process??
  // get ratio of height width
  // decide whether height or width is bigger
  //
}

void down_sample()
{
  
}

void init_markers()
{
  markers[0].sc = COLOR1;
  markers[0].red = 256;
  markers[0].blue = 256;
  markers[0].green = 256;
  markers[0].pixels = 0;
  
  markers[1].sc = COLOR2;
  markers[1].red = 256;
  markers[1].blue = 256;
  markers[1].green = 256;
  markers[1].pixels = 0;
  
  markers[2].sc = COLOR3;
  markers[2].red = 256;
  markers[2].blue = 256;
  markers[2].green = 256;
  markers[2].pixels = 0;
  
  markers[3].sc = COLOR4;
  markers[3].red = 256;
  markers[3].blue = 256;
  markers[3].green = 256;
  markers[3].pixels = 0;
  
  return;
}



int main(void)
{
  
  while(1)
  {
    
  }
  
  return 0;
}
