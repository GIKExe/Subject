#include <stdio.h>

int main() {
  int K, N, X, S=1;
  scanf("%d %d %d", &X, &K, &N);
  for (; N > 0; N--) {S*=K;}
  printf("%d", (X / S) % K);
  return 0;
}