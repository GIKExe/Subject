#include <stdio.h>

int main() {
	int a, b, x, c=0;
	scanf("%d %d", &a, &b);
	while (1) {
		int res = scanf("%d", &x);
		printf("\"%d\"\n", res);
		if (x >= a && x <= b) c++;
	}
	printf("%d", c);
	return 0;
}