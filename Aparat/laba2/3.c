#include "Arduino.h"
#include <stdbool.h>

#define RESET_PIN 2
#define CLOCK_PIN 3

void setup() {
	Serial.begin(9600);
	for (int i = 0; i < 3; i++) pinMode(i+2, OUTPUT);
	digitalWrite(RESET_PIN, 1);
	delay(10);
	digitalWrite(RESET_PIN, 0);
	for (int i = 0; i < 10; i++) {
		digitalWrite(CLOCK_PIN, 1);
		delay(5);
		digitalWrite(CLOCK_PIN, 0);
		delay(500);
	}
}

void loop() {

}




// https://pandia.org/text/79/290/images/image006_48.gif