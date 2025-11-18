#include <stdio.h>

int main() {
  double x; scanf("%lf", &x);
  if (x < 0) {printf("1"); x = -x;}
  else printf("0");
  int e = 15;
  int a = (int) x;
  double b = x - a;
  int i = 1;
  int j, k;
  if (a > 0) {
    for (; i*2 <= a && e<30; i*=2) e++;
    j = 25 - e;
    k = i / 2;
  } else {
    for (; b<1 && e>0; b*=2) e--;
    j = 10;
    b -= (int) b;
  }
  for (i=16; i>0; i/=2) printf("%d", e/i%2);
  if (a > 0) for (i=10; k>0 && i>0; k/=2, i--) printf("%d", a/k%2);
  for (; j>0; j--) {
    b = b * 2;
    a = (int) b;
    printf("%d", a);
    b = b - a;
  }
  return 0;
}