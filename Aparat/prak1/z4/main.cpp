#include "melody.h"

#define BUZZER_PIN 9

bool running = false;
bool first_selected = true;
unsigned int thisNote = 0;

void f1() {
  first_selected = !first_selected;
  running = false;
  thisNote = 0;
}

void f2() {
  running = !running;
}

void setup() {
  attachInterrupt(INT0, f1, RISING);
  attachInterrupt(INT1, f2, RISING);
  for (int i = 0; i < 3; i++)
    pinMode(4+i, OUTPUT);
}

Block *melody;
unsigned int melody_size;

void loop() {
  digitalWrite(4, first_selected);
  digitalWrite(5, !first_selected);

  if (!running) return;

  if (first_selected) {
    melody = melody_1;
    melody_size = melody_1_size;
  } else {
    melody = melody_2;
    melody_size = melody_2_size;
  }

  if (thisNote >= melody_size) {
    thisNote = 0;
    running = false;
    return;
  };

  int noteDuration = 1000 / melody[thisNote].temp;
  tone(BUZZER_PIN, melody[thisNote].note, noteDuration);
  digitalWrite(6, melody[thisNote].note > 0);
  delay(noteDuration);
  digitalWrite(6, 0);
  delay(noteDuration * 0.3);
  noTone(BUZZER_PIN);

  thisNote++;
}
