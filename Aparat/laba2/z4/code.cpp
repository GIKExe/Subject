#include <LiquidCrystal.h>

#define BTN_PIN 2
#define CON_PIN 3
#define RS_PIN 4
#define E_PIN 5
#define D4 6
#define D5 7
#define D6 8
#define D7 9
#define POT_PIN A0

#define MODES 4

LiquidCrystal lcd(RS_PIN, E_PIN, D4, D5, D6, D7);

int pot_old;
int readPot() {
  return map(analogRead(POT_PIN), 0, 1023, -1, 2);
}

const char text[] = "Success needs hard work today. Logic is key. Fast code wins. Stay calm. Read more.              ";
int chunk = 0;
int index = 0;
int mode = 0;

void f() {
  mode = (mode + 1) % MODES;
  analogWrite(CON_PIN, map(mode, 0, MODES-1, 0, 255));
}

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  pinMode(CON_PIN, OUTPUT);
  analogWrite(CON_PIN, 0);
  pinMode(POT_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(BTN_PIN), f, FALLING);
  pot_old = readPot();
}


void loop() {
  int pot = readPot();
  if (pot != 0 && pot_old == 0) {
    // pot in [-1, 1] and pot != 2
    chunk += pot;
    if (chunk < 0) chunk = 0;
    if (chunk > 4) chunk = 4;
  }
  pot_old = pot;

  if (index == 0) {
    lcd.setCursor(0, 0);
  } else if (index == 16) {
    lcd.setCursor(0, 1);
  }

  lcd.print(text[chunk * 16 + index]);

  index++;
  if (index > 31) index = 0;
}