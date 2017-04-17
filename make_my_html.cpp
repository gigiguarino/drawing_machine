
#include <iostream>
using namespace std;

int main()
{
  for (int i = 99; i >= 0; i--){
    for (int j = 0; j < 100; j++){
      cout << "<div class='pixel' data-x=" << j << " data-y=" << i << ">" << "</div>";
    }
  }
  
  return 0;
}
