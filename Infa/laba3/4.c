#include <stdio.h>
#include <math.h>

int main() {
  int x, y, i, n;
  char a, b, c;
  scanf("%d %d %d", &x, &y, &n);
  i = pow(2, n-1);
  if (x>=i || y>=i || x< -i || y < -i) {
    printf("ошибка"); return 0;}
  if (x<0) x+=i*2;
  if (y<0) y+=i*2;
  c = 0;
  for (; i>0; i/=2) {
    a = x / i % 2;
    b = y / i % 2;
    c += (a-b<0 ? -a+b : a-b);
  }
  printf("%d", c);
  return 0;
}