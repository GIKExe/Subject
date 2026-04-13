#include "Arduino.h"
#include <stdbool.h>

#define RESET_PIN 2
#define CLOCK_PIN_H 3
#define CLOCK_PIN_L 4

typedef unsigned char u8;

bool is_harshad_number(u8 num) {
	u8 x = num % 10 + num / 10 % 10;
	return num % x == 0;
}

void ping(u8 pin) {
	digitalWrite(pin, 1);
	digitalWrite(pin, 0);
}

bool checker(u8 pin, u8 num, u8 *x) {
	if ((*x) == num) return false;
	(*x) = ((*x) + 1) % 10;
	digitalWrite(pin, 1);
	return true;
}

void setup() {
	for (int i = 0; i < 3; i++) pinMode(i+2, OUTPUT);
	ping(RESET_PIN);
}

u8 num = 1;
u8 num_l = 0, num_h = 0;
void loop() {
	if (!is_harshad_number(num)) {
		num++;
		return;
	}

	if (num > 99) {
		ping(RESET_PIN);
		num = 1;
		num_l = 0;
		num_h = 0;
	}

	if (checker(CLOCK_PIN_L, num % 10, &num_l)
	 || checker(CLOCK_PIN_H, (num / 10) % 10, &num_h)) {
		digitalWrite(CLOCK_PIN_L, 0);
		digitalWrite(CLOCK_PIN_H, 0);
		return;
	}

	delay(1500);
	num++;
}