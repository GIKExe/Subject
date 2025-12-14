#include <stdio.h>
#include <math.h>

int main() {
  unsigned short n, i; unsigned int b, b2;
  scanf("%hu", &n);
  for (b=1; n > b*2; b*=2);
  for (i=0; i < n; i++) {
    for (b2=b; b2 > 0; b2/=2) printf("%d", i/b2%2);
    printf(" ");
  }
  return 0;
}