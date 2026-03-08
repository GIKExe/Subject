// https://codeforces.com/contest/2123/problem/C
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int n; scanf("%d", &n);
		int a[n]; scanf("%d", &a[0]);
		int pref_min[n];
		int suff_max[n];
		pref_min[0] = a[0];
		for (int i = 1; i < n; i++) {
			scanf("%d", &a[i]);
			pref_min[i] = (a[i] < pref_min[i-1] ? a[i] : pref_min[i-1]);
		}
		suff_max[n-1] = a[n-1];
		for (int i = n-2; i >= 0; i--) {
			suff_max[i] = (a[i] > suff_max[i+1] ? a[i] : suff_max[i+1]);
		}
		printf("1");
		for (int i = 1; i <= n-2; i++) {
			if (a[i] < pref_min[i-1] || a[i] > suff_max[i+1]) {
				printf("1");
			} else {
				printf("0");
			}
		}
		printf("1\n");
	}
	return 0;
}