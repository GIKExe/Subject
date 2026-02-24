# задание 1760C

for i in range(int(input())):
	input()
	l = [int(x) for x in input().split(" ")]
	print("Output: ", end='')
	for j,x in enumerate(l):
		l2 = l.copy()
		del l2[j]
		print(x - max(l2), ' ', end='')
	print()