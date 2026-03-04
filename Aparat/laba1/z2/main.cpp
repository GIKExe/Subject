void setup() {
	for (int i = 0; i < 3; i++) pinMode(i+2, INPUT_PULLUP);
	for (int i = 0; i < 3; i++) pinMode(i+5, OUTPUT);
}

void proc(unsigned char pin) {
	digitalWrite(pin+3, digitalRead(pin)); // Анодный RGB
}

int i = 0;
void loop() {
	if (i >= 3) i = 0;
	proc(i+2);
	i++;
}