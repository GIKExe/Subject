import math
import copy
from typing import List

Matrix = List[List[float]]
Vector = List[float]

class OptimizedNeuralNet:
    """Оптимизированная нейронная сеть прямого распространения на чистом Python.

    Этот класс реализует двухслойную полносвязную нейронную сеть с активацией ReLU 
    в скрытом слое и Softmax на выходе. Оптимизация достигнута за счет 
    предварительного транспонирования матриц весов для эффективного вычисления 
    скалярного произведения через встроенные итераторы Python.

    Complexity:
        Space: O(W), где W — общее количество весов и смещений (хранение весов и их транспонированных копий).
    """

    def __init__(self, weights_h: Matrix, bias_h: Vector, 
                 weights_o: Matrix, bias_o: Vector):
        """Инициализирует нейронную сеть и подготавливает веса для вычислений.

        Args:
            weights_h (Matrix): Матрица весов скрытого слоя размерности (input_dim, hidden_dim).
            bias_h (Vector): Вектор смещений скрытого слоя размерности (hidden_dim).
            weights_o (Matrix): Матрица весов выходного слоя размерности (hidden_dim, output_dim).
            bias_o (Vector): Вектор смещений выходного слоя размерности (output_dim).

        Complexity:
            Time: O(I * H + H * O), где I — входная размерность, H — скрытая, O — выходная.
        """
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
        """Проверяет соответствие размерностей матриц весов и векторов смещений.

        Raises:
            ValueError: Если количество векторов весов в транспонированной матрице 
                не совпадает с длиной соответствующего вектора смещений.
        """
        if len(self.w_h_t) != len(self.b_h):
            raise ValueError("Размерность скрытых весов не совпадает с bias_h")
        if len(self.w_o_t) != len(self.b_o):
            raise ValueError("Размерность выходных весов не совпадает с bias_o")

    def forward(self, x_batch: Matrix) -> Matrix:
        """Выполняет прямое распространение (inference) для батча данных.

        Процесс включает вычисление скрытого слоя с активацией ReLU, 
        выходного слоя (логитов) и применение функции Softmax.

        Args:
            x_batch (Matrix): Входные данные в виде матрицы (batch_size, input_dim).

        Returns:
            Matrix: Вероятностное распределение классов после Softmax (batch_size, output_dim).

        Complexity:
            Time: O(N * (I * H + H * O)), где N — размер батча, I — входная размерность, 
                H — скрытая, O — выходная.
            Space: O(N * (H + O)) для хранения промежуточных и финальных активаций батча.
        """
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