#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x20, 16, 2);
#define BUTTON_PIN 2
#define BATTERY_PIN A0
#define DIODE_DROP 0.7

int scrollPosition = 0;
bool directionForward = false;
unsigned long previousMillis = 0;
unsigned long startTime = 0;

String text;
int textLength;

String getRuntime() {
	char buffer[17];
	sprintf(buffer, "Elapsed: %5d s", millis() / 1000);
	return String(buffer);
}

void buildText() {
	text = "Battery voltage: ";
	float voltage = analogRead(BATTERY_PIN) / 1023.0 * 10.0;
	if (voltage > 0.1) voltage += DIODE_DROP;
	text += String(voltage);
	text += " Volts";
	textLength = text.length();
	text += "               ";
}

void setup() {
	Serial.begin(9600);
	lcd.init();
	lcd.backlight();
	lcd.clear();

	pinMode(BATTERY_PIN, INPUT);
	pinMode(BUTTON_PIN, INPUT_PULLUP);
	startTime = millis();

	buildText();
}

void loop() {
	static bool lastButtonState = HIGH;
	bool buttonState = digitalRead(BUTTON_PIN);
	if (lastButtonState == HIGH && buttonState == LOW) {
		directionForward = !directionForward;
		delay(10);
	}
	lastButtonState = buttonState;

	
	lcd.setCursor(0, 0);
	String displayText = text.substring(scrollPosition, scrollPosition + 16);
	lcd.print(displayText);


	if (directionForward) {
		scrollPosition++;
		if (scrollPosition >= textLength) {
			scrollPosition = 0;
			buildText();
		}
	} else {
		scrollPosition--;
		if (scrollPosition < 0) {
			scrollPosition = textLength - 1;
			buildText();
		}
	}

	lcd.setCursor(0, 1);
	lcd.print(getRuntime());

	delay(300);
}