#include <stdio.h>
#include <math.h>

int main() {
  float x, y=0;
  int a, b, ml, mk, s, l, k;
  scanf("%f %d %d", &x, &l, &k);
  s = 1;
  for (a=(int)x; a>0; a/=10) { 
    y += a%10 * s; s *= l; }
  ml = 0; s = 1;
  for (; x-(int)x>0; x*=10) {
    ml += 1; s *= l; }
  for (b=(int)x; s>1; b/=10) {
    y += b%10/(float)s;
    s/=l; }
  b = 0; s = 1;
  for (a=(int)y; a>0; a/=k) {
    b += a%k*s; s *= 10; }
  printf("%d", b);
  if (ml == 0) return 0;
  printf(".");
  y = y - (int)y; s = 10;
  mk = (int) ceil(ml * (log10(l)/log10(k)));
  for (; mk>0; mk--) {
    y *= k; a = (int)y;
    printf("%d", a); y -= a; }
  return 0;
}