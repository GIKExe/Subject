#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int n; scanf("%d\n", &n);
		int a[n], counter = 0;
		for (int i = 0; i < n; i++) a[i] = (getchar()-48) * -1;
		getchar();
		for (int i = 0; i < n; i++) {
			int x = getchar()-48;
			if (x != 1) continue;
			if (a[i] == 0) {
				a[i] = 1; counter++;
			} else {
				if (i > 0) {
					if (a[i-1] == -1) {
						a[i-1] = 1; counter++; continue; }
				}
				if (i < n-1) {
					if (a[i+1] == -1) {
						a[i+1] = 1; counter++; }
				}
			}
		}; printf("%d\n", counter);
	}; return 0;
}