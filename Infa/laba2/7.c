#include <stdio.h>
#include <string.h>

int main() {
  unsigned char A[256], H[256][256], c, i, j, n, g, x;

  n=1; g=0; i=0;
  while (i<=255) {
    A[i] = getchar();
    A[i+1] = 0;
    if (A[i] < 97 || A[i] > 122) break;
    x = 1;
    for (j=1; j<n; j++) {
      x = strcmp(A, H[j]);
      if (x == 0) { g=j; i++; break; }
    }; if (x == 0) continue;
    printf("(%hhu, %c) ", g, A[i]);
    strcpy(H[n], A);
    i = 0; g = 0; n++;
  }; if (g!=0) {
    printf("(0, %c) ", A[i-1]);
  }; return 0;
}