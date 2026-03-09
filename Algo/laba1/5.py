# https://codeforces.com/contest/1598/problem/C
from sys import stdin
from collections import defaultdict

t = int(stdin.readline())
for _ in range(t):
	n = int(stdin.readline())
	a = list(map(int, stdin.readline().split()))
	s = sum(a)
	
	if (2 * s) % n != 0:
		print(0); continue
			
	target = (2 * s) // n
	count = defaultdict(int)
	ans = 0
		
	for x in a:
		need = target - x
		ans += count[need]
		count[x] += 1
	print(ans)