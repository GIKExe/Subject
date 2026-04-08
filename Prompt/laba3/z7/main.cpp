#include <iostream>
#include <vector>
#include <iomanip>
#include "NeuralNetCpp.h"

int main() {
	try {
		// Определение весов (в реальной жизни они загружаются из файла)
		// Скрытый слой: 3 входа -> 4 нейрона
		NeuralNetCpp::Matrix weights_h = {
			{0.1f, 0.2f, 0.3f, 0.4f},
			{0.5f, 0.6f, 0.7f, 0.8f},
			{0.9f, 1.0f, 1.1f, 1.2f}
		};
		NeuralNetCpp::Vector bias_h = {0.1f, 0.1f, 0.1f, 0.1f};

		// Выходной слой: 4 входа -> 2 выхода (класса)
		NeuralNetCpp::Matrix weights_o = {
			{0.1f, 0.5f},
			{0.2f, 0.6f},
			{0.3f, 0.7f},
			{0.4f, 0.8f}
		};
		NeuralNetCpp::Vector bias_o = {0.0f, 0.0f};

		// Создаем экземпляр сети
		NeuralNetCpp net(weights_h, bias_h, weights_o, bias_o);

		// Входные данные (батч из 2-х примеров)
		NeuralNetCpp::Matrix input_batch = {
			{1.0f, 0.5f, -0.2f},
			{0.0f, 1.0f, 2.0f}
		};

		// Выполняем расчет
		auto results = net.forward(input_batch);

		// Вывод результатов
		std::cout << std::fixed << std::setprecision(4);
		std::cout << "Neural Network Results (Softmax):" << std::endl;
		for (size_t i = 0; i < results.size(); ++i) {
			std::cout << "Sample " << i << ": ";
			for (float prob : results[i]) {
				std::cout << prob << " ";
			}
			std::cout << std::endl;
		}

	} catch (const std::exception& e) {
		std::cerr << "Error: " << e.what() << std::endl;
		return 1;
	}

	return 0;
}

// g++ -std=c++17 -O3 -Wall main.cpp -o neural_net.exe