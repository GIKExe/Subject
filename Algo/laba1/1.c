// https://codeforces.com/contest/1760/problem/C
#include <stdio.h>

int main() {
	int i;
	scanf("%d", &i);
	for (; i > 0; i--) {
		int j, n; scanf("%d", &j); n = j;
		int a[j], fm = 0, fmi = -1, sm = 0;
		for (j = 0; j < n; j++) {
			scanf("%d", &a[j]);
			if (a[j] > fm) {
				sm = fm;
				fm = a[j];
				fmi = j;
			} else if (a[j] > sm) {
				sm = a[j];
			}
		}
		for (j = 0; j < n; j++)
			printf("%d ", a[j] - (j == fmi ? sm : fm));
		printf("\n");
	}
	return 0;
}