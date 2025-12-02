#include <stdio.h>
#include <math.h>

int main() {
  float x;
  int gs, ms, es,  sx, ex, n, digit, sex;
  scanf("%f %d %d", &x, &gs, &ms);
  es = gs - ms - 1;
  sx = 0;
  if (x < 0) {sx=1; x=-x;}
  printf("%d", sx);
  ex = pow(2, es-1);
  if (x != 0) {
    while (x >= 1) {x/=2; ex++;}
    while (x < 0.5) {x*=2; ex--;}
  }
  for (n=pow(2,ms-1); n>0; n/=2) {
    x*=2;
    digit = (int) x;
    x -= digit;
    printf("%d", digit);
  }
  for (n=pow(2,es-1); n>0; n/=2) {
    digit = ex/n%2;
    printf("%d", digit);
  }; return 0;
}