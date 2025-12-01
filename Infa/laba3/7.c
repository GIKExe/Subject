#include <stdio.h>
#include <math.h>

int main() {
  float x;
  int sx=0, ex, n, digit, c;
  scanf("%f", &x);
  if (x < 0) {sx=1; x = -x;}
  printf("%d ", sx);
  ex = 64;
  if (x == 0) ex = 0;
  else {
    for (; x>=1; x/=16) ex++;
    for (; x<0.0625; x*=16) ex--;
  }
  for (n=pow(2, 6); n>0; n/=2) {
    digit = ex/n%2;
    printf("%d", digit);
  }
  for (n=pow(2, 23), c=0; n>0; n/=2, c++) {
    // C - для лучшей читаемости
    if (c % 4 == 0) printf(" ");
    // выводит пробел каждые 4 символа
    x*=2;
    digit = (int) x;
    x = x - digit;
    printf("%d", digit);
  }
  return 0;
}