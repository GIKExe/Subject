import unittest
import math
from v2 import OptimizedNeuralNet

class TestOptimizedNeuralNet(unittest.TestCase):

	def setUp(self):
		"""Инициализация базовых параметров для тестов."""
		self.w_h = [[0.1, 0.2], [0.3, 0.4]]  # 2x2
		self.b_h = [0.5, 0.5]                # 2
		self.w_o = [[0.1], [0.2]]            # 2x1
		self.b_o = [0.0]                     # 1
		self.nn = OptimizedNeuralNet(self.w_h, self.b_h, self.w_o, self.b_o)

	def test_forward_logic(self):
		"""Проверка математической корректности прохода."""
		x = [[1.0, 1.0]]
		# Hidden: 
		# h1 = ReLU(1*0.1 + 1*0.3 + 0.5) = 0.9
		# h2 = ReLU(1*0.2 + 1*0.4 + 0.5) = 1.1
		# Output:
		# o1 = (0.9*0.1 + 1.1*0.2 + 0.0) = 0.31
		# Softmax от одного элемента всегда [1.0]
		result = self.nn.forward(x)
		self.assertAlmostEqual(result[0][0], 1.0, places=7)

	def test_deep_copy_protection(self):
		"""Проверка, что веса внутри класса защищены от изменений извне."""
		original_val = self.w_h[0][0]
		self.w_h[0][0] = 999.9  # Меняем внешний список
		
		# Внутренний вес не должен измениться (проверяем raw или через эффект)
		self.assertEqual(self.nn.w_h_raw[0][0], original_val, 
						 "Веса внутри класса изменились вместе с внешним списком!")

	def test_dimension_mismatch_init(self):
		"""Проверка защиты при создании объекта с битыми размерами."""
		bad_b_h = [0.5] # Должно быть 2
		with self.assertRaises(ValueError):
			OptimizedNeuralNet(self.w_h, bad_b_h, self.w_o, self.b_o)

	def test_dimension_mismatch_forward(self):
		"""Проверка защиты при подаче данных неверной размерности."""
		bad_input = [[1.0, 2.0, 3.0]] # Ожидается 2 входа
		with self.assertRaises(ValueError):
			self.nn.forward(bad_input)

	def test_empty_input(self):
		"""Обработка пустого батча."""
		with self.assertRaises(ValueError):
			self.nn.forward([])

	def test_relu_activation(self):
		"""Проверка, что отрицательные значения обнуляются."""
		# Ставим отрицательные веса, чтобы сумма была < 0
		nn_neg = OptimizedNeuralNet(
			weights_h=[[-1.0, -1.0]], 
			bias_h=[-1.0, -1.0], 
			weights_o=[[1.0], [1.0]], 
			bias_o=[0.0]
		)
		# Вход положительный, но сумма будет отрицательной
		res = nn_neg.forward([[1.0]])
		# Если ReLU сработал, hidden будет [0, 0], значит output [1.0]
		self.assertEqual(res[0][0], 1.0)

	def test_softmax_stability(self):
		"""Проверка численной стабильности (overflow)."""
		# Большие значения без вычитания max_logit вызвали бы ошибку exp()
		large_logits_w = [[1000.0, -1000.0]]
		nn_large = OptimizedNeuralNet(
			[[1.0, 1.0]], [0.0, 0.0],
			large_logits_w, [0.0, 0.0]
		)
		try:
			res = nn_large.forward([[1.0]])
			self.assertAlmostEqual(res[0][0], 1.0, places=5)
		except OverflowError:
			self.fail("Softmax не справился с большими числами (OverflowError)")

if __name__ == "__main__":
	unittest.main()