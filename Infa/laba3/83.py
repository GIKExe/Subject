import math

def f1():
  a = 77617; b = 33096
  c = 333.75 * b**6 + a**2*(
    11*a**2*b**2 - b**6 - 121*b**4 - 2
  ) + 5.5*b**8 + (a/(2*b))
  print(f"{c}\n")

def f2():
  a = 77617; b = 33096
  c = 21*b**2 - 2*a**2 + 55*b**4 - 10*a**2*b**2 + (a/(2*b))
  print(f"{c}\n")

def Q(x):
  y = abs(x - (x**2 + 1)**0.5) - 1 / (x + (x**2 + 1)**0.5)
  return y

def E(z):
  if z == 0: return 1
  r = (math.exp(z) - 1) / z
  return r

def f3(x):
  y = E(pow(Q(x), 2))
  print(y)

def main():
  f1()
  f2()
  f3(15.0)
  f3(16.0)
  f3(17.0)
  f3(9999.0)

if __name__ == "__main__":
  main()