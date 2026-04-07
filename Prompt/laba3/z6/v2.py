import math
from typing import List

# Определение типов для ясности
Matrix = List[List[float]]
Vector = List[float]

class OptimizedNeuralNet:
    """Оптимизированная нейронная сеть прямого распространения на чистом Python.

    Реализует двухслойную архитектуру: входной слой, скрытый слой (ReLU) 
    и выходной слой (Softmax). Оптимизирована за счет предварительного 
    транспонирования весов для ускорения скалярного произведения.

    Complexity:
        Space: O(W), где W — количество уникальных весов и смещений.
    """

    def __init__(self, weights_h: Matrix, bias_h: Vector, 
                 weights_o: Matrix, bias_o: Vector):
        """Инициализирует сеть, копирует и подготавливает веса.

        Args:
            weights_h (Matrix): Матрица весов скрытого слоя [input_dim][hidden_dim].
            bias_h (Vector): Вектор смещений скрытого слоя [hidden_dim].
            weights_o (Matrix): Матрица весов выходного слоя [hidden_dim][output_dim].
            bias_o (Vector): Вектор смещений выходного слоя [output_dim].

        Complexity:
            Time: O(I * H + H * O), где I, H, O — размерности слоев.
        """
        # ТРАНСПОНИРУЕМ веса сразу для оптимизации скалярного произведения в Python.
        # Теперь self.w_h_t[j] — это список весов для j-го нейрона от всех входов.
        self.w_h_t = list(map(list, zip(*weights_h)))
        self.b_h = list(bias_h)
        self.w_o_t = list(map(list, zip(*weights_o)))
        self.b_o = list(bias_o)
        
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """Проверяет соответствие размерностей весов и смещений.

        Raises:
            ValueError: Если количество векторов весов не совпадает с количеством смещений.
        """
        if len(self.w_h_t) != len(self.b_h):
            raise ValueError(f"Hidden layer mismatch: {len(self.w_h_t)} weight vectors vs {len(self.b_h)} biases")
        if len(self.w_o_t) != len(self.b_o):
            raise ValueError(f"Output layer mismatch: {len(self.w_o_t)} weight vectors vs {len(self.b_o)} biases")

    def forward(self, x_batch: Matrix) -> Matrix:
        """Выполняет прямой проход для батча данных.

        Args:
            x_batch (Matrix): Входные данные [batch_size][input_dim].

        Returns:
            Matrix: Распределение вероятностей после Softmax [batch_size][output_dim].

        Raises:
            ValueError: Если батч пуст или размерность входных данных не совпадает с весами.

        Complexity:
            Time: O(N * (I * H + H * O)), где N — размер батча.
        """
        if not x_batch or not x_batch[0]:
            raise ValueError("Input batch is empty")
        
        input_dim = len(self.w_h_t[0])
        if len(x_batch[0]) != input_dim:
            raise ValueError(f"Input dimension mismatch. Expected {input_dim}, got {len(x_batch[0])}")

        # Локальные переменные для ускорения доступа в цикле
        w_h_t, b_h = self.w_h_t, self.b_h
        w_o_t, b_o = self.w_o_t, self.b_o
        _exp = math.exp
        
        results = []
        for row in x_batch:
            # 1. Hidden Layer (ReLU)
            hidden = []
            for weights_vec, bias in zip(w_h_t, b_h):
                dot = sum(x * w for x, w in zip(row, weights_vec)) + bias
                hidden.append(dot if dot > 0 else 0.0)
            
            # 2. Output Layer (Logits)
            logits = []
            for weights_vec, bias in zip(w_o_t, b_o):
                dot = sum(h * w for h, w in zip(hidden, weights_vec)) + bias
                logits.append(dot)
            
            # 3. Softmax (Стабильная реализация)
            max_l = max(logits)
            exps = [_exp(l - max_l) for l in logits]
            sum_e = sum(exps)
            results.append([e / sum_e for e in exps])
            
        return results