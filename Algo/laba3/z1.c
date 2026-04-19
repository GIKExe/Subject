#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef unsigned long long u64;
#define LLONG_MAX 0x7fffffffffffffffLL
#define get_cost(a, b) (u64)abs(s[a][0] - s[b][0]) + (u64)abs(s[a][1] - s[b][1])

int main() {
	int t;
	scanf("%d", &t);
	for (; t > 0; t--) {
		int n, k, a, b;
		scanf("%d %d %d %d", &n, &k, &a, &b);
		int s[n+1][2]; 
		s[0][0] = 0;
		s[0][1] = 0;
		for (int i = 1; i <= n; i++) 
			scanf("%d %d", &s[i][0], &s[i][1]);
		u64 _cost, cost = get_cost(a, b);
		if (k < 2) {
			printf("%lld\n", cost);
			continue;
		}
		
		u64 ac = LLONG_MAX, bc = LLONG_MAX;
		for (int i = 1; i <= k; i++) {
			    _cost = get_cost(a, i);
			if (_cost < ac) ac = _cost;
			    _cost = get_cost(b, i);
			if (_cost < bc) bc = _cost;
		}

		_cost = ac+bc;
		if (_cost < cost) {
			printf("%lld\n", _cost);
		} else {
			printf("%lld\n", cost);
		}
	}
	return 0;
}