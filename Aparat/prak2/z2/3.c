#include <LiquidCrystal.h>

#define RS_PIN 2
#define RW_PIN 3
#define E_PIN 4
#define D4 5
#define D5 6
#define D6 7
#define D7 8

LiquidCrystal lcd(RS_PIN, RW_PIN, E_PIN, D4, D5, D6, D7);

byte char_I[8] = {17, 17, 19, 21, 25, 17, 17,  0};
byte char_G[8] = {31, 16, 16, 16, 16, 16, 16,  0};
byte char_L[8] = { 7,  9,  9,  9,  9,  9, 17,  0};
byte char_U[8] = { 4, 21, 17, 19, 21, 25, 17,  0};

void setup() {
  lcd.begin(16, 2);

  lcd.createChar(0, char_I);
  lcd.createChar(1, char_G);
  lcd.createChar(2, char_L);
  lcd.createChar(3, char_U);

  lcd.setCursor(0, 0);
  lcd.write(byte(0));
  lcd.print("BAH");

  lcd.setCursor(0, 1);
  lcd.write(byte(1));
  lcd.print("OPTO");
  lcd.write(byte(2));
  lcd.print("OME");
  lcd.write(byte(3));
}

void loop() {}