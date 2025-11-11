#include <stdio.h>
#include <math.h>

int main() {
  int n, m; scanf("%d %d", &n, &m);
  int a[n][m];
  float min;
  for (int i = 0; i < n; i++) {
    float s = 0;
    for (int j = 0; j < m; j++) {
      scanf("%d", &a[i][j]);
      s += a[i][j];
    }
    s = s / m;
    if (s < min || i == 0) min = s;
  }
  min = round(min*100);
  printf("%.2f", min/100);
  return 0;
}