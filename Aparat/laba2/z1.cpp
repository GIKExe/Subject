#include <Arduino.h>

#define BUTTON_PIN 2
#define CLOCK_PIN 4
#define RESET_PIN 5

bool is_composite(int n) {
  if (n < 4) return false;
  for (int i = 2; i < n; i++)
    if (n % i == 0) return true;
  return false;
}

void pulse(int pin) {
  digitalWrite(pin, HIGH);
  delay(10);
  digitalWrite(pin, LOW);
}

int c = 0;
void addc() {
  c++;
  pulse(CLOCK_PIN);
}

void reset() {
  c = 0;
  pulse(RESET_PIN);
  for (int i = 0; i < 4; i++) addc();
}

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(CLOCK_PIN, LOW);
  reset();
}

bool b = false;
void loop() {
  bool x = !digitalRead(BUTTON_PIN);
  if (x && !b) {
    addc();
    while (!is_composite(c)) {
      addc();
    }
    if (c > 99) reset();
  }
  b = x;
}