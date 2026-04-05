import math
import copy
from typing import List

Matrix = List[List[float]]
Vector = List[float]

class OptimizedNeuralNet:
	def __init__(self, weights_h: Matrix, bias_h: Vector, 
				 weights_o: Matrix, bias_o: Vector):
		# Глубокое копирование
		self.w_h_raw = copy.deepcopy(weights_h)
		self.b_h = copy.deepcopy(bias_h)
		self.w_o_raw = copy.deepcopy(weights_o)
		self.b_o = copy.deepcopy(bias_o)
		
		# ТРАНСПОНИРУЕМ веса заранее. 
		# Теперь self.w_h[j] — это вектор весов для j-го нейрона (все входы).
		# Это позволяет использовать sum(x * w for x, w in zip(row, weight_vector))
		self.w_h_t = list(map(list, zip(*self.w_h_raw)))
		self.w_o_t = list(map(list, zip(*self.w_o_raw)))
		
		self._validate_dimensions()

	def _validate_dimensions(self) -> None:
		if len(self.w_h_t) != len(self.b_h):
			raise ValueError("Размерность скрытых весов не совпадает с bias_h")
		if len(self.w_o_t) != len(self.b_o):
			raise ValueError("Размерность выходных весов не совпадает с bias_o")

	def forward(self, x_batch: Matrix) -> Matrix:
		# Локальные кэши
		w_h_t = self.w_h_t
		b_h = self.b_h
		w_o_t = self.w_o_t
		b_o = self.b_o
		
		# Кэшируем функции
		_exp = math.exp
		
		results = []
		for row in x_batch:
			# 1. Hidden Layer (ReLU)
			# Благодаря транспонированию мы итерируемся по вектору весов каждого нейрона
			hidden = []
			for weights_vec, bias in zip(w_h_t, b_h):
				# sum(a*b) через zip — самая быстрая конструкция в pure python для dot product
				dot = sum(x * w for x, w in zip(row, weights_vec)) + bias
				hidden.append(dot if dot > 0 else 0.0)
			
			# 2. Output Layer (Logits)
			logits = []
			for weights_vec, bias in zip(w_o_t, b_o):
				dot = sum(h * w for h, w in zip(hidden, weights_vec)) + bias
				logits.append(dot)
			
			# 3. Softmax (Инлайним для скорости)
			max_l = max(logits)
			exps = [_exp(l - max_l) for l in logits]
			sum_e = sum(exps)
			results.append([e / sum_e for e in exps])
			
		return results

# --- Пример использования тот же ---
if __name__ == "__main__":
	w_hidden = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
	b_hidden = [0.1, 0.1, 0.1]
	w_out = [[0.7, 0.8], [0.9, 1.0], [1.1, 1.2]]
	b_out = [0.0, 0.0]
	
	nn = OptimizedNeuralNet(w_hidden, b_hidden, w_out, b_out)
	input_data = [[1.0, 0.5], [0.2, 0.8]]
	
	output = nn.forward(input_data)
	for i, res in enumerate(output):
		print(f"Пример {i+1}: {[round(v, 4) for v in res]}")