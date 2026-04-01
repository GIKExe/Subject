#include "Arduino.h"

void setup() {
	for (int i = 0; i < 5+7; i++) pinMode(i+2, OUTPUT);
	for (int i = 0; i < 7; i++) digitalWrite(i+2+5, 1);
}

const unsigned char nabor[2][32][2] = {
	{
		{0, 6},
		{0, 5},
		{0, 4},
		{0, 3},
		{0, 2},
		{0, 1},
		{0, 0},
		{1, 0},
		{2, 0},
		{3, 0},
		{4, 0},
	},
	{
		{4, 0},
		{3, 0},
		{2, 0},
		{1, 0},
		{0, 0},
		{0, 1},
		{0, 2},
		{0, 3},
		{1, 3},
		{2, 3},
		{3, 3},
		{4, 3},
		{4, 4},
		{4, 5},
		{3, 5},
		{2, 5},
		{1, 5},
		{0, 5},
	}
};

void pix(int a, int b) {
	digitalWrite(a+2, 1);
	digitalWrite(b+2+5, 0);
	delay(1);
	digitalWrite(a+2, 0);
	digitalWrite(b+2+5, 1);
}

bool flag = false;
unsigned long long time = millis();
int index = 0;
void loop() {
	if (millis() - time > 1000) {
		flag = !flag;
		time = millis();
	}
		
	pix(nabor[(int) flag][index][0], nabor[(int) flag][index][1]);
	index++;
	if (flag) {
		if (index > 17) index = 0;
	} else {
		if (index > 11) index = 0;
	}
	
}