def f(a, b, c, d, e):
	g = [[sum(a[k] * b[k][j] for k in range(len(a))) + d[j] for j in range(len(b[0]))]]
	h = [[(1 / (1 + 2.7182818284 ** -x)) for x in y] for y in g][0]
	return [sum(h[k] * c[k][j] for k in range(len(h))) + e[j] for j in range(len(c[0]))]