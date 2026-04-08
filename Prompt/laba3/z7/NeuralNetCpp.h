#ifndef NEURAL_NET_CPP_H
#define NEURAL_NET_CPP_H

#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <numeric>
#include <string>

/**
 * @brief Оптимизированная нейронная сеть прямого распространения.
 * * Перенос класса OptimizedNeuralNet с Python на C++17.
 * Реализует архитектуру: Hidden Layer (ReLU) -> Output Layer (Softmax).
 */
class NeuralNetCpp {
public:
    using Matrix = std::vector<std::vector<float>>;
    using Vector = std::vector<float>;

    /**
     * @brief Конструктор с инициализацией и транспонированием весов.
     * * @param weights_h Веса скрытого слоя [input_dim][hidden_dim].
     * @param bias_h Смещения скрытого слоя [hidden_dim].
     * @param weights_o Веса выходного слоя [hidden_dim][output_dim].
     * @param bias_o Смещения выходного слоя [output_dim].
     */
    NeuralNetCpp(const Matrix& weights_h, const Vector& bias_h,
                 const Matrix& weights_o, const Vector& bias_o) {
        
        // Валидация входных размерностей
        if (weights_h.empty() || weights_h[0].empty()) throw std::invalid_argument("Empty hidden weights");
        if (weights_h[0].size() != bias_h.size()) {
            throw std::invalid_argument("Hidden layer mismatch: weights vs biases"); //
        }
        if (weights_o.empty() || weights_o[0].empty()) throw std::invalid_argument("Empty output weights");
        if (weights_o[0].size() != bias_o.size()) {
            throw std::invalid_argument("Output layer mismatch: weights vs biases"); //
        }

        input_dim_ = weights_h.size();
        hidden_dim_ = bias_h.size();
        output_dim_ = bias_o.size();

        // Реализуем транспонирование: weights[in][out] -> weights_t[out][in]
        // Это позволяет вычислять скалярное произведение как линейный проход по вектору.
        w_h_t_ = transpose(weights_h);
        b_h_ = bias_h;
        w_o_t_ = transpose(weights_o);
        b_o_ = bias_o;
    }

    /**
     * @brief Прямой проход (Inference) для батча данных.
     * * @param x_batch Входные данные [batch_size][input_dim].
     * @return Matrix Результат Softmax [batch_size][output_dim].
     */
    Matrix forward(const Matrix& x_batch) const {
        if (x_batch.empty()) throw std::invalid_argument("Input batch is empty"); //
        if (x_batch[0].size() != input_dim_) {
            throw std::invalid_argument("Input dimension mismatch. Expected " + std::to_string(input_dim_)); //
        }

        Matrix results;
        results.reserve(x_batch.size());

        for (const auto& row : x_batch) {
            // 1. Скрытый слой (ReLU)
            Vector hidden(hidden_dim_);
            for (size_t j = 0; j < hidden_dim_; ++j) {
                float dot = std::inner_product(row.begin(), row.end(), w_h_t_[j].begin(), 0.0f);
                dot += b_h_[j];
                hidden[j] = std::max(0.0f, dot); // ReLU
            }

            // 2. Выходной слой (Logits)
            Vector logits(output_dim_);
            for (size_t j = 0; j < output_dim_; ++j) {
                float dot = std::inner_product(hidden.begin(), hidden.end(), w_o_t_[j].begin(), 0.0f);
                logits[j] = dot + b_o_[j];
            }

            // 3. Стабильный Softmax
            float max_l = *std::max_element(logits.begin(), logits.end());
            float sum_e = 0.0f;
            Vector probs(output_dim_);
            
            for (size_t i = 0; i < output_dim_; ++i) {
                probs[i] = std::exp(logits[i] - max_l);
                sum_e += probs[i];
            }

            for (float& p : probs) {
                p /= sum_e;
            }

            results.push_back(std::move(probs));
        }

        return results;
    }

private:
    size_t input_dim_;
    size_t hidden_dim_;
    size_t output_dim_;

    // Транспонированные веса для оптимизации кэша
    // Транспонированные веса для оптимизации кэша
    Matrix w_h_t_; 
    Vector b_h_;
    Matrix w_o_t_;
    Vector b_o_;

    /**
     * @brief Вспомогательная функция транспонирования матриц.
     * Эквивалент Python: list(map(list, zip(*weights))).
     */
    Matrix transpose(const Matrix& src) const {
        if (src.empty()) return {};
        size_t rows = src.size();
        size_t cols = src[0].size();
        Matrix dst(cols, Vector(rows));
        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                dst[j][i] = src[i][j];
            }
        }
        return dst;
    }
};

#endif // NEURAL_NET_CPP_H