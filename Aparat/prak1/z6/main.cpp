#include <Arduino.h>

#define BUZZER_PIN 9
#define BUTTON_START 2
#define BUTTON_COUNT 5

void setup() {
	Serial.begin(9600);
	pinMode(BUZZER_PIN, OUTPUT);
	for (int i = 0; i < BUTTON_COUNT; i++)
		pinMode(BUTTON_START + i, INPUT_PULLUP);
}

volatile bool b[5];
volatile unsigned char index = 0;
const float m[] = {
	261.63,
	293.66,
	329.63,
	349.23,
	392.0,
};

void loop() {
	if (index >= BUTTON_COUNT) index = 0;
	bool btn = digitalRead(BUTTON_START + index);
	if (!btn && b[index])
		tone(BUZZER_PIN, m[index], 500);
	b[index] = btn;
	index++;
}