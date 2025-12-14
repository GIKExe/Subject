#include <stdio.h>

int main() {
  int x, r, i=0;
  char digits[21];
  scanf("%d", &x);
  if (x == 0) {printf("0"); return 0;}
  while (x != 0) {
    r = x % 3;
    if (r < 0) r += 3;
    x = (x - r) / 3;
    
    if (r == 2) {
      r = -1;
      x += 1;
    }

    switch (r) {
      case -1: digits[i] = 'n'; break;
      case  0: digits[i] = '0'; break;
      case  1: digits[i] = 'p'; break;
    } i++;
  }

  for (int j=i-1; j >= 0; j--)  printf("%c", digits[j]);
  return 0;
}