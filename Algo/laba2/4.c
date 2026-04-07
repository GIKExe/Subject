#include <stdio.h>
#include <stdbool.h>

int main() {
	int n, m; scanf("%d %d", &n, &m);
	int g[n+1], c = 0;
	for (int i = 0; i < n+1; i++) 
		g[i] = 0;

	for (int i = 0; i < m; i++) {
		int x, y; scanf("%d %d", &x, &y);
		g[x]++; g[y]++;
	}

	bool bus = true;
	bool star = false;
	for (int i = 1; i < n+1; i++) {
		if (g[i] == 1) {c++;}
		else if (g[i] == m) {star = true;}
		else if (g[i] > 2) {bus = false;}
	}
		
	if (star && c == n-1) {
		printf("star topology");
	} else if (bus && c == 0) {
		printf("ring topology");
	} else if (bus && c == 2) {
		printf("bus topology");
	} else {
		printf("unknown topology");
	}
	return 0;
}