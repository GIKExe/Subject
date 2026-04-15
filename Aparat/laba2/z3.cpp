#include "Arduino.h"
#include <stdbool.h>

#define RESET_PIN 12
#define CLOCK_PIN 11
typedef unsigned char u8;

bool is_not_harshad(u8 number) {
  if (number == 0) return true;
  u8 x = number % 10 + number / 10 % 10;
  return number % x != 0;
}

void setup() {
  pinMode(RESET_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  digitalWrite(RESET_PIN, 1);
  digitalWrite(RESET_PIN, 0);
}

u8 number = 0;
void loop() {
  number = (number + 1) % 100;
  digitalWrite(CLOCK_PIN, 1);
  digitalWrite(CLOCK_PIN, 0);
  if (is_not_harshad(number)) return;
  delay(1500);
}