#include <stdio.h>

int main() {
  long n; scanf("%ld", &n);
  long a[n];
  long o = 0;
  for (long i = 0; i < n; i++) {
    scanf("%ld", &a[i]);
    if (a[i] < 0) { o = i; break; }
  }
  if (o == 0) { printf("No"); return 0;}
  for (long i = 0; i < o; i++) {
    if (a[i] <= a[i + 1]) { printf("No"); return 0; }
  }
  printf("Yes"); return 0;
}