#define FIRST_LED_PIN 2
#define LAST_LED_PIN 11

void setup() {
  for (int pin = FIRST_LED_PIN; pin <= LAST_LED_PIN; ++pin)
    pinMode(pin, OUTPUT);
}

void loop() {
  unsigned int ms = millis();
  int i =  + (ms / 120) % 10;
    if (i > 4) i = 9 - i;
  digitalWrite(FIRST_LED_PIN + i, HIGH);
    digitalWrite(FIRST_LED_PIN + (9 - i), HIGH);
  delay(10);
  digitalWrite(FIRST_LED_PIN + i, LOW);
    digitalWrite(FIRST_LED_PIN + (9 - i), LOW);
}