#include <stdio.h>
#include <math.h>

int main() {
  int X, M;
  scanf("%d %d", &X, &M);
  if (X >= pow(2, M)) {
    printf("ошибка"); return 0;
  }
  for (; M > 0; M--) {
    printf("%d", X / (int) pow(2, M-1) % 2);
  }
  return 0;
}