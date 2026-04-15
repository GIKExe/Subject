#define BUZZER_PIN 10
#define PLAYERS 2
#define START_LED 4
#define LEDS 3

void blinking(int s) {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < LEDS; j++)
      digitalWrite(j+START_LED+s*LEDS, HIGH);
    delay(500);
    for (int j = 0; j < LEDS; j++)
      digitalWrite(j+START_LED+s*LEDS, LOW);
    delay(500);
  }
}

char counters[PLAYERS];
bool buttons[PLAYERS];

void setup() {
  Serial.begin(9600);
  srand(micros());
  pinMode(BUZZER_PIN, OUTPUT);
  for (int i = 0; i < LEDS*PLAYERS; i++)
    pinMode(i+START_LED, OUTPUT);
  for (int i = 0; i < PLAYERS; i++) {
    pinMode(i+2, INPUT_PULLUP);
    counters[i] = 0;
  }
}

void loop(){
  delay(random(2000, 7000));
  // 3 килогерца, 250 миллисекунд
  tone(BUZZER_PIN, 3000, 250); 

  for (int i = 0; i < PLAYERS; i++)
    buttons[i] = true;

  for (int p = 0;; p = (p+1) % PLAYERS) {
    // если игрок номер «player» нажал кнопку...
    bool btn = !digitalRead(p+2);
    if (btn && !buttons[p]) {
      // ...включаем его светодиод и сигнал победы на 1 сек
      digitalWrite(counters[p]+START_LED+p*LEDS, HIGH);
      counters[p]++;
      tone(BUZZER_PIN, 4000, 1000);
      delay(1000);
      if (counters[p] >= LEDS) {
        blinking(p);
        for (int i = 0; i < LEDS*PLAYERS; i++)
          digitalWrite(i+START_LED, LOW);
        for (int i = 0; i < PLAYERS; i++)
          counters[i] = 0;
      }
      break;
    }
    buttons[p] = btn;
  }
}
