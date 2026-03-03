#define LED_PIN 3
#define RESISTOR_PIN A0

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(RESISTOR_PIN, INPUT);
}

// >1000 - макс.
// 890-910 - ср.
// 160-350 - мин.
void loop() {
  int x = analogRead(RESISTOR_PIN);
  x -= 200;
  if (x < 0) x=0;
  if (x > 800) x=800;
  float p = (800 - x) / 800.0;
  unsigned char l = (255 * p);
  analogWrite(LED_PIN, l);
  delay(100);
}