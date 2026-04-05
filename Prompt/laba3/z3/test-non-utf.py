import time
import random
from typing import List, Tuple

# Импортируем классы из файлов
from v1 import PurePythonNeuralNet as SimpleNet
from v2 import OptimizedNeuralNet as OptNet


def generate_matrix(rows: int, cols: int) -> List[List[float]]:
	"""Генерирует случайную матрицу заданного размера."""
	return [[random.random() for _ in range(cols)] for _ in range(rows)]

def generate_vector(size: int) -> List[float]:
	"""Генерирует случайный вектор."""
	return [random.random() for _ in range(size)]

def run_benchmark():
	# Параметры теста
	input_dim = 500
	hidden_dim = 500
	output_dim = 10
	batch_size = 5  # Небольшой батч, так как матрицы 500x500 в Pure Python очень тяжелые
	
	print(f"--- Инициализация данных ({input_dim}x{hidden_dim}) ---")
	w_h = generate_matrix(input_dim, hidden_dim)
	b_h = generate_vector(hidden_dim)
	w_o = generate_matrix(hidden_dim, output_dim)
	b_o = generate_vector(output_dim)
	x_batch = generate_matrix(batch_size, input_dim)

	# Тест 1: Простая версия
	print("Запуск SimpleNet (1.py)...")
	net1 = SimpleNet(w_h, b_h, w_o, b_o)
	start_time = time.perf_counter()
	res1 = net1.forward(x_batch)
	end_time = time.perf_counter()
	time_simple = end_time - start_time
	print(f"Время выполнения SimpleNet: {time_simple:.4f} сек")

	# Тест 2: Оптимизированная версия
	print("Запуск OptimizedNet (2.py)...")
	net2 = OptNet(w_h, b_h, w_o, b_o)
	start_time = time.perf_counter()
	res2 = net2.forward(x_batch)
	end_time = time.perf_counter()
	time_opt = end_time - start_time
	print(f"Время выполнения OptimizedNet: {time_opt:.4f} сек")

	# Сравнение
	speedup = (time_simple - time_opt) / time_simple * 100
	print("\n--- Результаты ---")
	print(f"Ускорение: {speedup:.2f}%")
	
	# Проверка идентичности результатов (с учетом погрешности float)
	diff = sum(abs(res1[0][i] - res2[0][i]) for i in range(output_dim))
	if diff < 1e-9:
		print("Валидация: Результаты идентичны.")
	else:
		print(f"Валидация: Есть расхождения (diff={diff:.2e})")

if __name__ == "__main__":
	run_benchmark()