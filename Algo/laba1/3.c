// https://codeforces.com/contest/2123/problem/C
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int n; scanf("%d", &n);
		int a[n]; scanf("%d", &a[0]);
		int pm[n], sm[n];
		pm[0] = a[0];
		for (int i = 1; i < n; i++) {
			scanf("%d", &a[i]);
			pm[i] = (a[i] < pm[i-1] ? a[i] : pm[i-1]);
		}
		sm[n-1] = a[n-1];
		for (int i = n-2; i >= 0; i--)
			sm[i] = (a[i] > sm[i+1] ? a[i] : sm[i+1]);
		printf("1");
		for (int i = 1; i <= n-2; i++)
			printf(a[i] < pm[i-1] || a[i] > sm[i+1] ? "1" : "0");
		printf("1\n");
	}
	return 0;
}