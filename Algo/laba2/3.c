#include <stdio.h>

int main() {
	int t; scanf("%d", &t);
	for (; t > 0; t--) {
		int n, k; scanf("%d %d", &n, &k);
		if (k == n*n || n*n - k > 1) {
			printf("YES\n");
			int counter = 0;
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					if (counter < k) {
						if (j == 0) {printf("U");}
						else {printf("L");}
					} else {
						if (i == n-1 && j == n-1) {printf("L");}
						else if (j == n-1) {printf("D");}
						else {printf("R");}
					}
					counter++;
				}; printf("\n");
			}
		} else printf("NO\n");
	}; return 0;
}