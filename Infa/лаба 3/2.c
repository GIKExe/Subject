#include <stdio.h>
#include <math.h>

int main() {
  int x, n, i;
  scanf("%d %d", &x, &n);
  i = pow(2, n-1);
  if (x >= i || x <= -i) {printf("ошибка"); return 0;}
  if (x<0) x=2*i+x-1;
  for (; i>0; i/=2) printf("%d", x/i%2);
  return 0;
}