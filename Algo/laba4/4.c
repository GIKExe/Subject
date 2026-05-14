// https://codeforces.com/contest/2227/problem/E
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t>0; t--) {
		int n; scanf("%d", &n);
		int a[n];
		for (int i = 0; i < n; i++) scanf("%d", &a[i]);
		

		if (a[n-1] <= a[n-2] && a[n-1] > 0) {
			a[n-1]--;
		} else if (a[n-2] < a[n-1] && a[n-2] > 0) {
			a[n-2]--;
		}

		int sum = 0;
		for (int i = n-2; i >= 0; i--) {
			if (a[i] > a[i+1]) {
				sum += a[i] - a[i+1];
				a[i] = a[i+1];
			}
		}
		printf("%d\n", sum);
	}
	return 0;
}