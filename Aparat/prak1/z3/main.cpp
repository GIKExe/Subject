#include <Arduino.h>

void setup() {
	pinMode(3, OUTPUT);
	pinMode(14, INPUT);
	Serial.begin(9600);
}

// >1000 - мас.
// 890-910 - ср.
// 160-350 - мин.
void loop() {
	int x = analogRead(14);
	x -= 200;
	if (x < 0) x=0;
	if (x > 800) x=800;
	float p = (800 - x) / 800.0;
	unsigned char l = (255 * p);
	analogWrite(3, l);
	Serial.println((int) l);
	delay(100);
}