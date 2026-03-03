#define BUZZER_PIN 9
#define BUTTON_START 2
#define BUTTON_COUNT 5

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  for (int i = 0; i < BUTTON_COUNT; i++)
    pinMode(BUTTON_START + i, INPUT_PULLUP);
}

volatile bool b[5];
volatile unsigned char index = 0;
const unsigned short m[] = {
  130, 147, 164, 174, 196,
};

void loop() {
  if (index >= BUTTON_COUNT) index = 0;
  bool btn = digitalRead(BUTTON_START + index);
  if (!btn && b[index])
    tone(BUZZER_PIN, m[index], 500);
  b[index] = btn;
  index++;
}