#include <stdio.h>

int main() {
  int n; scanf("%d", &n);
  int A[n];
  int s=0, f=0; float fs=0;
  for (int i = 0; i < n; i++) {
    scanf("%d", &A[i]);
    if (A[i]%3 == 0) s++;
    if (A[i]%2 == 0) {fs++; f+=A[i];}
  }
  float a = f/fs;
  int b = (int)(a < 0 ? a-0.5 : a+0.5);
  printf("%d ", s);
  for (int i = 0; i < n; i++) printf("%d ", A[i]);
  printf("%d", b);
  return 0;
}