#include <stdio.h>
#include <stdlib.h>

#define MAXN 200005

int pos[MAXN], arr[MAXN];
int cnt = 0;

int main() {
    int N, M, K;
    if (scanf("%d %d %d", &N, &M, &K) != 3) return 0;

    for (int i = 1; i <= N; ++i) {
        pos[i] = i;
        arr[i] = i;
    }

    int u, v;
    for (int step = 0; step < M; ++step) {
        scanf("%d %d", &u, &v);

        int t1 = arr[u];
        int t2 = arr[v];

        if (abs(pos[t1] - t1) > K) cnt--;
        if (abs(pos[t2] - t2) > K) cnt--;

        arr[u] = t2;
        arr[v] = t1;
        pos[t1] = v;
        pos[t2] = u;

        if (abs(pos[t1] - t1) > K) cnt++;
        if (abs(pos[t2] - t2) > K) cnt++;

        printf("%d\n", cnt > 0 ? 1 : 0);
    }

    return 0;
}