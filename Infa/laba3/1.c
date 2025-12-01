#include <stdio.h>
#include <math.h>

int main() {
  long x, n, i;
  scanf("%ld %ld", &x, &n);
  i = pow(2, n-1);
  if (x >= i || x < -i) {printf("ошибка"); return 0;}
  if (x<0) x+=i*2;
  for (; i>0; i/=2) printf("%d", x/i%2);
  return 0;
}