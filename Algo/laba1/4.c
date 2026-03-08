// https://codeforces.com/contest/522/problem/B
#include <stdio.h>

int main() {
	int n; scanf("%d", &n);
	int sum = 0, w[n], h[n];
	int fm = 0, fmi = -1, sm = 0;
	for (int i = 0; i < n; i++) {
		scanf("%d", &w[i]);
		scanf("%d", &h[i]);
		sum += w[i];
		if (h[i] > fm) {
			sm = fm;
			fm = h[i];
			fmi = i;
		} else if (h[i] > sm) {
			sm = h[i];
		}
	}
	for (int i = 0; i < n; i++)
		printf("%d ", (sum - w[i])*(i == fmi ? sm : fm));
	return 0;
}