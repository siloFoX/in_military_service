#include <iostream>

using namespace std;

int main() {
  // ios_base::sync_with_studio(false);
  // cin.tie(NULL);

  int A, B, C;
  cin >> A >> B >> C;

  cout << (A + B) % C << endl;
  cout << ((A % C) + (B % C)) % C << endl;
  cout << (A * B) % C << endl;
  cout << ((A % C) * (B % C)) % C;

  return 0;
}