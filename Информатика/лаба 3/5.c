#include <stdio.h>
#include <math.h>

int main() {
  int mx, my, mz;
  unsigned char ex, ey, sx, sy;
  unsigned short x=0, y=0, z, i;
  for (i=32768; i>0; i/=2) {scanf("%1hu", &z); x+=i*z;}
  for (i=32768; i>0; i/=2) {scanf("%1hu", &z); y+=i*z;}
  sx = x / 32768 % 2;
  sy = y / 32768 % 2;
  ex = x / 1024 % 32;
  ey = y / 1024 % 32;
  mx = x % 1024 + 1024;
  my = y % 1024 + 1024;
  if (ex>ey) {
    my/=pow(2, ex-ey); ey = ex;
  } else {
    mx/=pow(2, ey-ex); ex = ey;
  }
  if (sx>0) mx = -mx;
  if (sy>0) my = -my;
  mz = mx + my;
  if (mz<0) {mz=-mz; printf("1");}
  else printf("0");
  
  while (mz/1024 != 1 && mz!=0) {
    if (mz/1024==0) { mz/=2; ex++; }
    else { mz*=2; ex--; }
  }
  for (i=32; i>0; i/=2) printf("%d", ex/i%2);
  for (i=1024; i>0; i/=2) printf("%d", mz/i%2);
  return 0;
}