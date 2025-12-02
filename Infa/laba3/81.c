#include <stdio.h>
#include <math.h>

void f1() {
  double a = 77617, b = 33096;
  double c = 333.75 * pow(b,6) + pow(a,2)*(
    11*pow(a,2)*pow(b,2) - pow(b,6) - 121*pow(b,4) - 2
  ) + 5.5*pow(b,8) + (a/(2*b));
  printf("%f\n\n", c);
}

void f2() {
  double a = 77617, b = 33096;
  double c = 21*pow(b,2) - 2*pow(a,2)
  + 55*pow(b,4) - 10*pow(a,2)*pow(b,2) + (a/(2*b));
  printf("%f\n\n", c);
}

double Q(double x) {
  double y = fabs(x - pow(pow(x,2) + 1, 0.5))
  - 1 / (x + pow(pow(x,2) + 1, 0.5));
  return y;
}

double E(double z) {
  if (z == 0) return 1;
  double r = (exp(z) - 1) / z;
  return r;
}

void f3(double x) {
  double y = E(pow(Q(x), 2));
  printf("%f\n", y);
}

int main() {
  f1();
  f2();
  f3(15.0);
  f3(16.0);
  f3(17.0);
  f3(9999.0);
  return 0;
}