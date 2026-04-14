#include <stdbool.h>

#define FIRST_PIN 2

typedef unsigned char u8;
typedef unsigned short u16;

const u8 digit[] = {
	0b00111111, // 0
	0b00000110, // 1
	0b01011011, // 2
	0b01001111, // 3
	0b01100110, // 4
	0b01101101, // 5
	0b01111101, // 6
	0b00000111, // 7
	0b01111111, // 8
	0b01101111, // 9
};

u16 get_x(u16 val) {
	return ((u16)digit[val / 10 % 10]) | ((u16)digit[val % 10] << 7);
}

u8 g[20] = {0, 1};
u8 g_size = 2;
void setup() {
	Serial.begin(9600);
	for (int i = 0; i < 14; i++)
		pinMode(i+FIRST_PIN, OUTPUT);
	for (int i = 2; i < 20; i++) {
		g[i] = g[i-1] + g[i-2];
		if (g[i] > 99) break;
		g_size++;
	}
}

int num_index = 0;
int index = 0;
bool drawing = true;
volatile u16 x = get_x(g[num_index]);
void loop() {
	if (drawing) {
		digitalWrite(index+FIRST_PIN, (x >> index) & 1);
		index++;
		if (index > 13) {
			drawing = false;
			index = 0;
			delay(1500);
		}
	} else {
		num_index = (num_index + 1) % g_size;
		x = get_x(g[num_index]);
		Serial.print(millis());
		Serial.print(" ");
		Serial.println(g[num_index]);
		drawing = true;
	}
}