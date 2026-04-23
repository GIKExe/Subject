#include "Arduino.h"

int leftDirPin = 4;
int leftSpeedPin = 5;

const int sensorPins[3] = {2, 8, 10};
const int ledPins[3] = {9, 11, 12};

void setup() {
  Serial.begin(9600);

  pinMode(leftDirPin, OUTPUT);
  pinMode(leftSpeedPin, OUTPUT);

  for (int i = 0; i < 3; i++) {
    pinMode(sensorPins[i], INPUT_PULLUP);
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  analogWrite(leftSpeedPin, 0);
}

void loop() {
  // {2, 8, 10}
  bool active[3];

  for (int i = 0; i < 3; i++) {
    active[i] = (digitalRead(sensorPins[i]) == LOW);
    digitalWrite(ledPins[i], active[i]);
  }

  if ((active[2]) && (active[0] || active[1])) {
    Serial.println("Активация мотора!");
    digitalWrite(leftDirPin, 1);
    analogWrite(leftSpeedPin, 127);
  } else {
    analogWrite(leftSpeedPin, 0);
  }
  for (int i = 0; i < 3; i++) {
    Serial.print(active[i] ? "1 " : "0 ");
  }
  Serial.println();

  delay(100);
}
