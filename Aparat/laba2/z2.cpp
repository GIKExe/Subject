#include "Arduino.h"
#include <stdbool.h>

#define LED_START 3

const unsigned char digit[] = {
  0b00111111, // 0
  0b00000110, // 1
   0b01011011, // 2
  0b01001111, // 3
   0b01100110, // 4
  0b01101101, // 5
  0b01111101, // 6
  0b00000111, // 7
  0b01111111, // 8
  0b01101111, // 9
};

// Проверка, является ли число двоичным палиндромом (без ведущих нулей)
bool is_palindrome_bin(unsigned int n) {
  if (n == 0) return true;
  unsigned int reversed = 0, original = n;
  while (n > 0) {
    reversed = (reversed << 1) | (n & 1);
    n >>= 1;
  }
  return original == reversed;
}

unsigned int num = 0;
unsigned char index = 0;

void f(){
  num++;
}

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 14; i++) pinMode(i+LED_START, OUTPUT);
  for (int i = 0; i < 14; i++) digitalWrite(i+LED_START, 1);
  pinMode(2, INPUT_PULLUP);
  attachInterrupt(INT0, f, FALLING);
}

void loop() {
  if (!is_palindrome_bin(num)) {
    num++;
    if (num > 99) {
      num = 0;
    }
    return;
  }
  unsigned char a, b;
  a = digit[num % 10];
  b = digit[num / 10 % 10];
  digitalWrite(index+LED_START, !((a >> index) & 1));
  digitalWrite(index+LED_START+7, !((b >> index) & 1));
  index++;
  if (index > 6) index = 0;
}

