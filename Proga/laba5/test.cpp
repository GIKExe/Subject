#include <iostream>
#include <algorithm> // для std::sort

int main() {
    char buffer[] = "9876543210";
    int size = sizeof(buffer) - 1; // -1, чтобы исключить нулевой символ \0

    // Сортировка массива
    std::sort(buffer, buffer + size);

    std::cout << "Отсортированный массив: " << buffer << std::endl;
    return 0;
}


// g++ test.cpp -o test