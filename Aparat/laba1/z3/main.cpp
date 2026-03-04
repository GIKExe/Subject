#define BUZZER_PIN 0
#define FIRST_BAR_PIN 4
#define BAR_COUNT 14

volatile unsigned short score = 3 << 6;
void pushP1() { score/=2; }
void pushP2() { score*=2; }

void setup() {
	for (int i = 0; i < BAR_COUNT; ++i)
		pinMode(i + FIRST_BAR_PIN, OUTPUT);
	pinMode(BUZZER_PIN, OUTPUT);
	attachInterrupt(INT0, pushP1, FALLING);
	attachInterrupt(INT1, pushP2, FALLING);
}

void loop() {
	tone(BUZZER_PIN, 2000, 1000);
	while (score > 1 && score < (1 << 13)) {
		for (int i = 0; i < BAR_COUNT; i++) {
			digitalWrite(FIRST_BAR_PIN + i, (score >> i) & 1);
		}
	}
	tone(BUZZER_PIN, 2000, 1000);
	while (true) {}
}