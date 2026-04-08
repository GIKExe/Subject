#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>
#include "NeuralNetCpp.h"

// Вспомогательная функция для сравнения чисел с плавающей точкой
bool is_close(float a, float b, float tol = 1e-4f) {
    return std::abs(a - b) < tol;
}

// Макрос для визуализации результатов теста
#define ASSERT_TEST(condition, name) \
    if (condition) { std::cout << "[PASS] " << name << std::endl; } \
    else { std::cout << "[FAIL] " << name << std::endl; return false; }

/**
 * @brief Тест 1: Сценарий из документации (README.md)
 */
bool test_documentation_example() {
    // Архитектура: 2 входа -> 3 скрытых (ReLU) -> 2 выхода (Softmax)
    NeuralNetCpp::Matrix w_h = {{0.1f, 0.2f, 0.3f}, {0.4f, 0.5f, 0.6f}};
    NeuralNetCpp::Vector b_h = {0.1f, 0.1f, 0.1f};
    NeuralNetCpp::Matrix w_o = {{0.7f, 0.8f}, {0.9f, 1.0f}, {1.1f, 1.2f}};
    NeuralNetCpp::Vector b_o = {0.0f, 0.0f};

    NeuralNetCpp nn(w_h, b_h, w_o, b_o);
    NeuralNetCpp::Matrix input = {{1.0f, 0.5f}};

    // Ожидаемый вывод: [0.4588, 0.5412]
    auto result = nn.forward(input);
    
    bool ok = is_close(result[0][0], 0.4588f) && is_close(result[0][1], 0.5412f);
    ASSERT_TEST(ok, "Documentation Example Match");
    return ok;
}

/**
 * @brief Тест 2: Проверка пустого батча
 */
bool test_empty_batch() {
    NeuralNetCpp nn({{0.1f}}, {0.1f}, {{0.1f}}, {0.1f});
    try {
        nn.forward({}); // Ожидается исключение
    } catch (const std::invalid_argument& e) {
        ASSERT_TEST(true, "Empty Batch Exception Handled");
        return true;
    }
    ASSERT_TEST(false, "Empty Batch Exception Failed");
    return false;
}

/**
 * @brief Тест 3: Неверная размерность входных данных
 */
bool test_dimension_mismatch() {
    // Сеть ждет 2 входа
    NeuralNetCpp nn({{0.1f, 0.1f}, {0.1f, 0.1f}}, {0.1f, 0.1f}, {{0.1f}, {0.1f}}, {0.1f});
    try {
        nn.forward({{1.0f, 2.0f, 3.0f}}); // Подаем 3 вместо 2
    } catch (const std::invalid_argument& e) {
        ASSERT_TEST(true, "Dimension Mismatch Exception Handled");
        return true;
    }
    ASSERT_TEST(false, "Dimension Mismatch Exception Failed");
    return false;
}

/**
 * @brief Тест 4: Проверка ReLU и Softmax (случайный набор)
 */
bool test_logic_and_activation() {
    // Тест аналогичен test_relu_activation из Python
    // Отрицательные веса должны привести к обнулению через ReLU
    NeuralNetCpp nn({{-1.0f, -1.0f}}, {-1.0f, -1.0f}, {{1.0f}, {1.0f}}, {0.0f});
    
    auto res = nn.forward({{1.0f}});
    // Если ReLU сработал: hidden = [0, 0], output = Softmax([0]) = [1.0]
    bool ok = is_close(res[0][0], 1.0f);
    ASSERT_TEST(ok, "ReLU Zeroing and Softmax Unity");
    return ok;
}

int main() {
    std::cout << "--- Starting NeuralNetCpp Tests ---" << std::endl;
    
    bool all_passed = true;
    all_passed &= test_documentation_example();
    all_passed &= test_empty_batch();
    all_passed &= test_dimension_mismatch();
    all_passed &= test_logic_and_activation();

    std::cout << "-----------------------------------" << std::endl;
    if (all_passed) {
        std::cout << "OVERALL STATUS: ALL TESTS PASSED" << std::endl;
        return 0;
    } else {
        std::cout << "OVERALL STATUS: SOME TESTS FAILED" << std::endl;
        return 1;
    }
}