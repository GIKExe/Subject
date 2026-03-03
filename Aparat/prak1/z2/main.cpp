#define CONTROL_PIN 3

int brightness = 0;
void setup() {
  pinMode(CONTROL_PIN, OUTPUT); 
}

bool to_half = true;
void loop() {
  analogWrite(CONTROL_PIN, brightness);
  delay(10);
  brightness++;
  if (brightness > 127 && to_half) {
    brightness = 0; 
    to_half = false;
  }
  if (brightness > 255) {
    brightness = 0; 
    to_half = true;
  }
}