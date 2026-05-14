// https://codeforces.com/contest/2227/problem/A
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int x, y; scanf("%d %d", &x, &y);
		printf(x%2 + y%2 > 1 ? "no\n" : "yes\n");
	}
	return 0;
}