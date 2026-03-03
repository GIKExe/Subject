#include <Arduino.h>

#define BUZZER_PIN 3
#define LDR_PIN A0

void setup() {
	pinMode(BUZZER_PIN, OUTPUT);
	Serial.begin(9600);
}

void loop() {
	int val = analogRead(LDR_PIN);
	Serial.println(val);
	// int frequency = map(val, 400, 500, 130, 247);
	int frequency = map(val, 400, 500, 1000, 2000);
	tone(BUZZER_PIN, frequency, 20);
	delay(100);
}