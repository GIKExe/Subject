#include <stdio.h>

unsigned int n;

int main() {
  scanf("%u", &n);
  int A[n];
  for (int i = 0; i < n; i++) scanf("%d", &A[i]);
  for (int i = 0; i < n; i++) {
    if (A[i] == 0) {
      int ia=i-1, ib=i-2;
      if (ia < 0) ia += n; if (ib < 0) ib += n;
      printf("%d ", A[ia] + A[ib]);
    } else printf("%d ", A[i]);
  }
  return 0;
}