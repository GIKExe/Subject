#include <stdio.h>

#define MAX 1000000

int f(int n) {
  if (n < 10) return n;
  int res = 1;
  while (n > 0) {
    int x = n % 10;
    n /= 10;
    if (x == 0) continue;
    res *= x; 
  }
  return res;
}

int g(int n) {
  if (n < 10) return n;
  return g(f(n));
}

int prefix[MAX+1][10];

int main() {
  for (int i = 1; i <= MAX; ++i) {
    int val = g(i);
    prefix[i][val]++;
  }

  for (int i = 1; i <= MAX; ++i) {
    for (int j = 1; j <= 9; ++j) 
      prefix[i][j] += prefix[i-1][j];
  }

  int t;
  scanf("%d", &t);
  for (; t > 0; t--) {
    int l, r, k;
    scanf("%d %d %d", &l, &r, &k);
    int answer = prefix[r][k] - prefix[l-1][k];
    printf("%d\n", answer);
  }
  return 0;
}