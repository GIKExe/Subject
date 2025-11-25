#include <stdio.h>
#include <math.h>
#include <stdlib.h>

// Функция для очистки экрана
void clear(void) {
#ifdef _WIN32
  system("cls");
#else
  system("clear");
#endif
}

// Функция для вычисления значения кривой в точке x
double f(double x) {
  return 2 * pow(x, 3) + pow(x, 2) + 1;
}

// Функция вычисления интеграла методом Симпсона
double simpson_integral(double a, double b, int n) {
  double h = (b - a) / n;
  double sum = f(a) + f(b);

  for (int i = 1; i < n; i++) {
    double x = a + i * h;
    if (i % 2 == 0)
      sum += 2 * f(x);
    else
      sum += 4 * f(x);
  }
  return sum * h / 3;
}

// Процедура для оценки погрешности методом Рунге (передача n по ссылке)
void estimate_error(double a, double b, int* n, double* error) {
  double integral_n = simpson_integral(a, b, *n);
  double integral_2n = simpson_integral(a, b, *n * 2);
  *error = fabs(integral_2n - integral_n) / 15;
}

int main() {
  double a = 0, b = 0, result, error;
  int n = 0, choice;
  int limits_set = 0, n_set = 0, integral_set = 0, error_set = 0;

  do {
    printf("\nМеню:\n");
    printf("1. Ввести пределы интегрирования (a, b)");
    limits_set ? printf(" (%f, %f)\n", a, b) : printf("\n");
    printf("2. Ввести количество разбиений n");
    n_set ? printf(" (%d)\n", n) : printf("\n");
    if (limits_set && n_set) {
      printf("3. Вычислить интеграл");
      integral_set ? printf(" (%.6f)\n", result) : printf("\n");
      printf("4. Оценить погрешность");
      error_set ? printf(" (%.6f)\n", error) : printf("\n");
      printf("5. Выход\n");
    } else {
      printf("3. [Недоступно - введите данные]\n");
      printf("4. [Недоступно - введите данные]\n");
      printf("5. Выход\n");
    }
    printf("Выберите опцию: ");
    scanf("%d", &choice);
    clear();

    switch (choice) {
      case 1:
        printf("Введите пределы интегрирования (a b): ");
        if (scanf("%lf %lf", &a, &b) == 2) {
          limits_set = 1;
          // printf("Пределы установлены: a=%.2f, b=%.2f\n", a, b);
        } else {
          printf("Ошибка ввода!\n");
          while (getchar() != '\n'); // Очистка буфера
        }
        break;

      case 2:
        printf("Введите количество разбиений n: ");
        if (scanf("%d", &n) == 1 && n > 0) {
          n_set = 1;
          // printf("Количество разбиений установлено: n=%d\n", n);
        } else {
          printf("Ошибка ввода! n должно быть положительным числом.\n");
          while (getchar() != '\n'); // Очистка буфера
        }
        break;

      case 3:
        if (limits_set && n_set) {
          result = simpson_integral(a, b, n);
          // printf("Результат интегрирования: %.6f\n", result);
          integral_set = 1;
        } else printf("Сначала введите данные!\n");

        break;

      case 4:
        if (limits_set && n_set) {
          estimate_error(a, b, &n, &error);
          // printf("Оценка погрешности: %.6f\n", error);
          // printf("Рекомендуемое количество разбиений: %d\n", n * 2);
          error_set = 1;
          n *= 2; // Увеличиваем n для следующего вычисления
        } else printf("Сначала введите данные!\n");
        break;

      case 5:
        printf("Выход...\n");
        break;

      default:
        printf("Неверный ввод! Выберите пункт от 1 до 5.\n");
    }
  } while (choice != 5);

  return 0;
}