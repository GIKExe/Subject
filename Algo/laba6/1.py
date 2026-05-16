x = int(input())
w = 10**9 + 7
a = x // 2
y = pow(3, a, w)
if x % 2 == 0:
    result = (y * 2) % w
else:
    result = (y * 4) % w
print(result)