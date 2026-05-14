// https://codeforces.com/contest/2227/problem/B
#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int n; scanf("%d\n", &n);
		int a = 0;
		int b = 0;
		for (; n > 0; n--) {
			char x = getchar();
			if (x == '(') a++;
			if (x == ')') b++;
		}
		printf(a != b ? "no\n" : "yes\n");
	}
	return 0;
}