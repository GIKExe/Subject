#include <stdio.h>

int main() {
  int n; scanf("%d", &n);
  int a[n], i, ni, s = 0;
  for (i = 0; i < n; i++) {
    scanf("%d", &a[i]);
    if (a[i] == 0) ni = i;
  }
  i = ni - 1;
  while (a[i] != 0) {
    s += a[i]; i--;
  }
  printf("%d", s);
  return 0;
}