#include <Arduino.h>
#define INITIAL -100
#define BUTTON_DELAY 50
#define FIRST_BAR_PIN 4
#define BAR_COUNT 14
#define MAX_SCORE 8

volatile int score = 0;
volatile unsigned long b1t = 0;
void b1_event() {
	unsigned long t = millis();
	if (t - b1t > BUTTON_DELAY) {
		// Serial.println("Кнопка 1 нажата");
		score--;
		b1t = t;
	}
}

volatile unsigned long b2t = 0;
void b2_event() {
	unsigned long t = millis();
	if (t - b2t > BUTTON_DELAY) {
		// Serial.println("Кнопка 2 нажата");
		score++;
		b2t = t;
	}
}

void setup() {
	Serial.begin(9600);
	pinMode(2, INPUT); // b1
	pinMode(3, INPUT); // b2
	attachInterrupt(INT0, b1_event, FALLING);
	attachInterrupt(INT1, b2_event, FALLING);
	for (int i=0; i<14; i++) {
		pinMode(4+i, OUTPUT);
	}
}

void loop() {
	while (abs(score) < MAX_SCORE) {
		int bound = map(score, -MAX_SCORE, MAX_SCORE, 0, BAR_COUNT);
		int left = min(bound, BAR_COUNT / 2 - 1);
		int right = max(bound, BAR_COUNT / 2);
		for (int i = 0; i < BAR_COUNT; ++i)
			digitalWrite(i + FIRST_BAR_PIN, i >= left && i <= right);
	}
	Serial.print("Player ");
	Serial.print(score > 0 ? "2" : "1");
	Serial.println(" win!");
	while (true) {}
}