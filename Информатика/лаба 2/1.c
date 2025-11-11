#include <stdio.h>

int main()
{
  unsigned int x, res=0;
  scanf("%d", &x);
  do {
    res += (1 - x % 2);
    x = x / 2;
  } while (x > 0);
  printf("%d", res);
  return 0;
}