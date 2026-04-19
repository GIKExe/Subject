#include <stdio.h>

int main() {
  int n, p;
  scanf("%d %d", &n, &p);

  int o[n+1], f[n+1], w[n+1], x = 0;

  for (int i = 1; i <= n; i++) {
    f[i] = 0; o[i] = 0; }

  for (int i = 1; i <= p; i++) {
    int a, b, d;
    scanf("%d %d %d", &a, &b, &d);
    f[a] = b; w[a] = d; o[b] = a;
  }

  if (p == 0 || p == n) {
    printf("0"); return 0; }

  for (int i = 1; i <= n; i++)
    if (f[i] != 0 && o[i] == 0) x++;
  printf("%d\n", x);

  for (int i = 1; i <= n; i++) {
    if (o[i] != 0 || f[i] == 0) continue;
    printf("%d ", i);
    int md = 1000000, j = i; 
    while (f[j] != 0) {
      if (w[j] < md) md = w[j];
      j = f[j];
    }
    printf("%d ", j);
    printf("%d\n", md);
  }

  return 0;
}