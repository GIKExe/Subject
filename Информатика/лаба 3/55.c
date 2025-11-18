#include <stdio.h>
#include <math.h>

unsigned short read() {
  unsigned short x = 0, z;
  for (int i=32768; i>0; i/=2) {
    scanf("%1hu", &z); x += i * z; }
  return x;
}

int main() {
  unsigned short x=read(), y=read(), z, i;
  char sx = x / 32768, sy = y / 32768;
  char ex = x / 1024 % 32, ey = y / 1024 % 32;
  int mx = x % 1024 + 1024, my = y % 1024 + 1024;

  if (ex>ey) { my>>=ex-ey; ey=ex; }
  else { mx>>=ey-ex; ex=ey; }

  if (sx) mx = -mx;
  if (sy) my = -my;

  int mz = mx + my;
  char sz = mz<0;
  if (sz) mz = -mz;
  printf("%d", sz);

  if (!mz) ex = 0;
  else {
    while (mz < 1024) { mz<<=1; ex--; }
    while (mz >= 2048) { mz>>=1; ex++; }
  }

  for (i=16; i>0; i>>=1) printf("%d", (ex>>(int)log2(i))&1);
  for (i=512; i>0; i>>=1) printf("%d", (mz>>(int)log2(i))&1);
  return 0;
}