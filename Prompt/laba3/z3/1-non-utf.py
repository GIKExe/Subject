import math
import copy
from typing import List

# Типы для аннотаций
Matrix = List[List[float]]
Vector = List[float]

class PurePythonNeuralNet:
	"""
	Высокопроизводительная реализация MLP на чистом Python.
	Логика активации вынесена в отдельные методы, данные инкапсулированы через копирование.
	"""

	def __init__(self, weights_h: Matrix, bias_h: Vector, 
				 weights_o: Matrix, bias_o: Vector):
		# Используем deepcopy, чтобы изменения во внешних списках не влияли на модель
		self.w_h = copy.deepcopy(weights_h)
		self.b_h = copy.deepcopy(bias_h)
		self.w_o = copy.deepcopy(weights_o)
		self.b_o = copy.deepcopy(bias_o)
		
		self._validate_dimensions()

	@staticmethod
	def relu(x: float) -> float:
		"""Функция активации ReLU."""
		return x if x > 0 else 0.0

	@staticmethod
	def softmax(logits: Vector) -> Vector:
		"""Численно стабильный Softmax."""
		max_l = max(logits)
		# Считаем экспоненты один раз
		exps = [math.exp(l - max_l) for l in logits]
		sum_exps = sum(exps)
		return [e / sum_exps for e in exps]

	def _validate_dimensions(self) -> None:
		"""Проверка размерностей весов и смещений."""
		if not self.w_h or not self.w_h[0]:
			raise ValueError("Матрица весов скрытого слоя пуста.")
		
		hidden_dim = len(self.w_h[0])
		if len(self.b_h) != hidden_dim:
			raise ValueError(f"Размер bias_h ({len(self.b_h)}) != {hidden_dim}.")
		
		if len(self.w_o) != hidden_dim:
			raise ValueError(f"Строки weights_o ({len(self.w_o)}) != {hidden_dim}.")
			
		output_dim = len(self.w_o[0])
		if len(self.b_o) != output_dim:
			raise ValueError(f"Размер bias_o ({len(self.b_o)}) != {output_dim}.")

	def forward(self, x_batch: Matrix) -> Matrix:
		"""
		Выполняет прямой проход для батча.
		"""
		if not x_batch or len(x_batch[0]) != len(self.w_h):
			raise ValueError("Размерность входа не совпадает с весами сети.")

		# Кэширование в локальные переменные для скорости
		w_h = self.w_h
		b_h = self.b_h
		w_o = self.w_o
		b_o = self.b_o
		
		# Кэширование методов активации
		relu = self.relu
		softmax = self.softmax
		
		h_dim = len(b_h)
		o_dim = len(b_o)
		input_dim = len(w_h)
		
		results = []
		
		for row in x_batch:
			# 1. Hidden Layer
			hidden = []
			for j in range(h_dim):
				# dot product: row @ col_j(w_h)
				z = sum(row[i] * w_h[i][j] for i in range(input_dim)) + b_h[j]
				hidden.append(relu(z))
			
			# 2. Output Layer
			logits = []
			for j in range(o_dim):
				# dot product: hidden @ col_j(w_o)
				z = sum(hidden[i] * w_o[i][j] for i in range(h_dim)) + b_o[j]
				logits.append(z)
			
			# 3. Softmax
			results.append(softmax(logits))
			
		return results

# --- Пример использования ---
if __name__ == "__main__":
	w_hidden = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
	b_hidden = [0.1, 0.1, 0.1]
	
	w_out = [[0.7, 0.8], [0.9, 1.0], [1.1, 1.2]]
	b_out = [0.0, 0.0]
	
	nn = PurePythonNeuralNet(w_hidden, b_hidden, w_out, b_out)
	
	input_data = [[1.0, 0.5], [0.2, 0.8]]
	
	try:
		output = nn.forward(input_data)
		for i, res in enumerate(output):
			formatted_res = [round(val, 4) for val in res]
			print(f"Пример {i+1} Softmax output: {formatted_res}")
	except ValueError as e:
		print(f"Ошибка: {e}")