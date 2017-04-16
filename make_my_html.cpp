
#include <iostream>
using namespace std;

int main()
{
  
  
  
  
  for (int i = 0; i < 100; i++)
  {
    for (int j = 0; j < 100; j++)
    {
      cout << "<div id = 'r" << i << "c" << j << "'>" << "</div>" << endl;
    }
    
    cout << "<br>" << endl;
  }
  
  return 0;
}
