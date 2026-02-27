#include <Arduino.h>

void setup() {
	for (int i = 0; i < 3; i++) pinMode(i+2, INPUT_PULLUP);
	pinMode(7, OUTPUT);
}

void loop() {
	bool a = !digitalRead(2);
	bool b = !digitalRead(3);
	bool c = !digitalRead(4);
	digitalWrite(7, (a && b) || (a && c) || (b && c));
}