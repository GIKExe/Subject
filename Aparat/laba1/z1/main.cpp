void setup() {
	pinMode(2, INPUT_PULLUP); // левая = a
	pinMode(3, INPUT_PULLUP); // правая = b
	pinMode(4, OUTPUT);
}

bool flag = false;
void loop() {
	short a = digitalRead(2);
	short b = digitalRead(3);
	if (!a && b) {
		if (flag) {
			digitalWrite(4, 0);
			delay(200);
		} else {
			digitalWrite(4, 1);
		}
		flag = false;
	} else if (a && !b) {
		flag = true;
	}
}