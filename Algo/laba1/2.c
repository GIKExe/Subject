// https://codeforces.com/contest/1807/problem/D
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t --) {
		int n, q, x;
		scanf("%d %d", &n, &q);
		long long a[n+1];
		a[0] = 0;
		for (int i = 0; i < n; i++) {
			scanf("%d", &x);
			a[i+1] = a[i] + x;
		}
		for (; q > 0; q--) {
			int l, r, k;
			scanf("%d %d %d", &l, &r, &k);
			int sum = a[n] - a[r] + a[l-1] + k*(r-l+1);
			printf(sum % 2 != 0 ? "YES\n" : "NO\n");
		}
	}
	return 0;
}