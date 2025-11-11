
#include <stdio.h>
#include <math.h>

int main() {
  int x, n, l; unsigned int y;
  scanf("%d %d", &x, &n);
  l = pow(2, n-1);
  if ((x > l-1) || (x < -l)) {
    printf("ошибка"); return 0;
  }
  // if (x < 0) x = x | l*2;
  y = (unsigned int) x;
  for (; l > 0; l/=2) {
    printf("%d", y/l%2);
  };
  return 0;
}