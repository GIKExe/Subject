#include <stdio.h>

int cnv(int X) {
  if (X>64 && X<91) { return X-55; }
  else if (X>47 && X<58) { return X-48; }
  else if (X>41 && X<59 && X!=44) { return X-3; }
  else if (X>35 && X<38) { return X+1; }
  else if (X==32) { return X+4; }
  else { return -1; }
}

int main() {
  int A, B, C, D, Z;
  while (1) {
    B = getchar();
    B = cnv(B);
    if (B==-1) break;
    A = B;
    B = getchar();
    B = cnv(B);
    if (B==-1) { C = A; Z = 32;   }
    else {  C = A*45+B; Z = 1024; }
    for (; Z>0; Z/=2) {
      D = C / Z % 2;
      printf("%d", D);
    }
    if (B==-1) break;
  }; return 0;
}