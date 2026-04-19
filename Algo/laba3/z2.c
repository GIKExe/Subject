// https://codeforces.com/contest/520/problem/B
#include <stdio.h>

int main() {
  int n, m, counter = 0;
  scanf("%d %d", &n, &m);
  while (m > n) {
    if (m % 2 == 0) {
      m /= 2;
    } else {
      m++;
    }
    counter++;
  }
  counter += n - m;
  printf("%d", counter);
  return 0;
}