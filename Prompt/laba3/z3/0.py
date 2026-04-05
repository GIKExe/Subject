import math
from typing import List, Union

# Типы для наглядности
Matrix = List[List[float]]
Vector = List[float]

class PurePythonNeuralNet:
	"""
	Высокопроизводительная реализация прямого прохода MLP на чистом Python.
	Архитектура: Input -> Hidden (ReLU) -> Output (Softmax).
	"""

	def __init__(self, weights_h: Matrix, bias_h: Vector, 
				 weights_o: Matrix, bias_o: Vector):
		self.w_h = weights_h  # [input_dim x hidden_dim]
		self.b_h = bias_h    # [hidden_dim]
		self.w_o = weights_o  # [hidden_dim x output_dim]
		self.b_o = bias_o    # [output_dim]
		
		self._validate_dimensions()

	def _validate_dimensions(self) -> None:
		"""Проверка размерностей весов и смещений."""
		if not self.w_h or not self.w_h[0]:
			raise ValueError("Матрица весов скрытого слоя пуста.")
		
		hidden_dim = len(self.w_h[0])
		if len(self.b_h) != hidden_dim:
			raise ValueError(f"Размер bias_h ({len(self.b_h)}) не совпадает с hidden_dim ({hidden_dim}).")
		
		if len(self.w_o) != hidden_dim:
			raise ValueError(f"Строки weights_o ({len(self.w_o)}) должны совпадать с hidden_dim ({hidden_dim}).")
			
		output_dim = len(self.w_o[0])
		if len(self.b_o) != output_dim:
			raise ValueError(f"Размер bias_o ({len(self.b_o)}) не совпадает с output_dim ({output_dim}).")

	def forward(self, x_batch: Matrix) -> Matrix:
		"""
		Выполняет прямой проход для батча данных.
		:param x_batch: Список списков (batch_size x input_dim)
		:return: Результат Softmax (batch_size x output_dim)
		"""
		if not x_batch or len(x_batch[0]) != len(self.w_h):
			raise ValueError("Размерность входных данных не соответствует весам.")

		# Кэшируем ссылки на методы и атрибуты в локальные переменные для ускорения доступа
		w_h = self.w_h
		b_h = self.b_h
		w_o = self.w_o
		b_o = self.b_o
		
		h_dim = len(b_h)
		o_dim = len(b_o)
		
		results = []
		
		for row in x_batch:
			# 1. Hidden Layer: Dot product + Bias
			# h = ReLU(x @ w_h + b_h)
			hidden = []
			for j in range(h_dim):
				# Считаем взвешенную сумму (dot product) вручную
				summ = sum(row[i] * w_h[i][j] for i in range(len(row))) + b_h[j]
				# ReLU activation
				hidden.append(summ if summ > 0 else 0.0)
			
			# 2. Output Layer: Dot product + Bias
			# logits = hidden @ w_o + b_o
			logits = []
			for j in range(o_dim):
				summ = sum(hidden[i] * w_o[i][j] for i in range(h_dim)) + b_o[j]
				logits.append(summ)
			
			# 3. Softmax
			# Используем shift-invariant Softmax для численной стабильности (вычитаем max)
			max_logit = max(logits)
			exps = [math.exp(l - max_logit) for l in logits]
			sum_exps = sum(exps)
			softmax_row = [e / sum_exps for e in exps]
			
			results.append(softmax_row)
			
		return results

# --- Пример использования ---
if __name__ == "__main__":
	# 2 входа, 3 скрытых нейрона, 2 выхода
	w_hidden = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
	b_hidden = [0.1, 0.1, 0.1]
	
	w_out = [[0.7, 0.8], [0.9, 1.0], [1.1, 1.2]]
	b_out = [0.0, 0.0]
	
	nn = PurePythonNeuralNet(w_hidden, b_hidden, w_out, b_out)
	
	# Входной батч (2 примера)
	input_data = [[1.0, 0.5], [0.2, 0.8]]
	
	try:
		output = nn.forward(input_data)
		for i, res in enumerate(output):
			formatted_res = [round(val, 4) for val in res]
			print(f"Пример {i+1} Softmax output: {formatted_res}")
	except ValueError as e:
		print(f"Ошибка размерностей: {e}")