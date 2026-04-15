#include "Arduino.h"
#include <LiquidCrystal.h>

// пины на МЭЛТ идут 
// с 14 по 1, 16, 15.
#define RS_PIN 2
#define E_PIN 3
#define D4 8
#define D5 9
#define D6 10
#define D7 11

LiquidCrystal lcd(RS_PIN, E_PIN, D4, D5, D6, D7);

void setup() {
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("\xA5" "BAH");
  lcd.setCursor(0, 1);
  lcd.print("\xA1OPTO\xA7OME\xA6");
}

void loop() {}