#define BUZZER_PIN 3
#define LDR_PIN A0

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  int val = analogRead(LDR_PIN);
  int frequency = map(val, 400, 500, 130, 247);
  tone(BUZZER_PIN, frequency, 20);
  delay(100);
}