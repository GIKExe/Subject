#include <stdio.h>
#include <math.h>

int read(int n) {
  int x = 0, digit;
  n = pow(2, n-1);
  for (; n>0; n/=2) {
    scanf("%1d", &digit);
    x += digit * n; }
  return x;
}

int main() {
  int sx, ex, mx, sy, ey, my;
  int sz, ez, mz, n, digit;
  scanf("%1d", &sx);
  ex = read(5);
  mx = read(10);
  mx = (mx+1024)*pow(-1, sx);
  scanf("%1d", &sy);
  ey = read(5);
  my = read(10);
  my = (my+1024)*pow(-1, sy);

  if (ex>ey) {
    my = my / pow(2, ex-ey);
    ez = ex;
  } else {
    mx = mx / pow(2, ey-ex);
    ez = ey;
  }
  mz = mx + my;
  sz = 0;
  if (mz == 0) ez = 0;
  else {
    if (mz < 0) {mz=-mz; sz=1;}
    while (mz < 1024) {mz*=2; ez--;}
    while (mz >= 2048) {mz/=2; ez++;}
  }
  printf("%d ", sz);
  for (n=16; n>0; n/=2) {
    digit = ez / n % 2;
    printf("%d", digit);
  } printf(" ");
  for (n=512; n>0; n/=2) {
    digit = mz / n % 2;
    printf("%d", digit);
  }
  return 0;
}