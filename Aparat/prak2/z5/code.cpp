
#include <stdbool.h>

#define LE 2

bool is_prime(int n) {
	if (n < 2) return false;
	for (int i = 2; i * i <= n; ++i)
		if (n % i == 0) return false;
	return true;
}

bool is_semiprime(int n) {
	if (n < 2) return false;
	for (int i = 2; i * i <= n; ++i) {
		if (n % i == 0) {
			if (is_prime(i) && is_prime(n / i))
				return true;
		}
	}
	return false;
}


void write_data(unsigned char b, unsigned char start) {
	digitalWrite(LE, 1);
	digitalWrite(3+start, b & 1);
	digitalWrite(4+start, (b >> 1) & 1);
	digitalWrite(5+start, (b >> 2) & 1);
	digitalWrite(6+start, (b >> 3) & 1);
	digitalWrite(LE, 0);
}

void setup(){
	Serial.begin(9600);
	pinMode(LE, OUTPUT);
	for (int i = 0; i < 8; i++) 
		pinMode(i+2, OUTPUT);
}

int num = 0;
void loop() {
	if (!is_semiprime(num)) {
		num = (num + 1) % 100;
		return;
	}

	write_data(num % 10, 0);
	write_data(num / 10 % 10, 4);
	delay(1500);
	num = (num + 1) % 100;
}