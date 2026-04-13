
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x20, 16, 2);
#define BUTTON_PIN 2

String text = "This is a scrolling text!               ";

int scrollPosition = 0;
int textLength = text.length() - 15;
bool directionForward = false;
unsigned long previousMillis = 0;
unsigned long startTime = 0;

void f() {
  //Serial.println("BTN");
  directionForward = !directionForward;
}

String getRuntime() {
  char buffer[17];
  sprintf(buffer, "Elapsed: %5d s", millis() / 1000);
  return String(buffer);
}

void setup() {
  //Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  startTime = millis();
}

void loop() {
  static bool lastButtonState = HIGH;
  bool buttonState = digitalRead(BUTTON_PIN);
  if (lastButtonState == HIGH && buttonState == LOW) {
    f();
	delay(10);
  }
  lastButtonState = buttonState;
	
  String displayText = text.substring(scrollPosition, scrollPosition + 16);
  lcd.setCursor(0, 0);
  lcd.print(displayText);

  if (directionForward) {
    scrollPosition++;
    if (scrollPosition >= textLength) {
      scrollPosition = 0;
    }
  } else {
    scrollPosition--;
    if (scrollPosition < 0) {
      scrollPosition = textLength - 1;
    }
  }

  lcd.setCursor(0, 1);
  lcd.print(getRuntime());

  delay(300);
}