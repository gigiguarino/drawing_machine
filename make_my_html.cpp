
#include <iostream>
using namespace std;

int main()
{
  for (int i = 199; i >= 0; i--){
    for (int j = 0; j < 200; j++){
      cout << "<div class='pixel' data-x=" << i << " data-y=" << j << ">" << "</div>" << endl;
    }
    cout << "<br>" << endl;
  }
  
  return 0;
}
