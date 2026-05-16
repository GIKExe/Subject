#include <stdio.h>
#include <string.h>

#define max_sclad 100000

int main() {
  int n; scanf("%d", &n);
  int a[max_sclad+1][2];
  for (int i = 0; i < max_sclad; i++) {
    a[i+1][0] = 0x7fffffff;
    a[i+1][1] = 0;
  }
  for (; n > 0; n--) {
    int sn, an; scanf("%d %d", &sn, &an);
    for (; an > 0; an--) {
      int art, dpr; scanf("%d %d", &art, &dpr);
      if ((dpr < a[art][0]) || (dpr == a[art][0] && sn < a[art][1])) {
        a[art][0] = dpr;
        a[art][1] = sn;
      }      
    }
  }
  int k; scanf("%d", &k);
  for (; k > 0; k--) {
    int art, pr; scanf("%d %d", &art, &pr);
    if (a[art][1] == 0) {
      printf("-1 -1\n");
      continue;
    }
    printf("%d %d\n", a[art][1], pr+a[art][0]);
  }
  return 0;
}