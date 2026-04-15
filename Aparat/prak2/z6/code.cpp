#define DS 4
#define ST_CP 5
#define SH_CP 6
#define MR 7

typedef unsigned char u8;
typedef unsigned short u16;

const u8 digit[] = {
  // G -> A
  0b01111110, 0b00001100, 0b10110110, 0b10011110, 0b11001100,
  0b11011010, 0b11111010, 0b00001110, 0b11111110, 0b11011110,
};

u8 g[100];

void setup() {
  Serial.begin(9600);
  pinMode(DS, OUTPUT);
  pinMode(ST_CP, OUTPUT);
  pinMode(SH_CP, OUTPUT);
  pinMode(MR, OUTPUT);

  for (u8 i = 0; i < 100; i++)
    g[i] = (i % 2 == 0 ? 0 : i);
  for (u8 i = 3; i < 100; i++) {
    if (g[i] == 0) continue;
    u8 counter = 0;
    for (u8 j = 0; j < 100; j++) {
      if (g[j] != 0) counter++;
      if (counter == i) {
        g[j] = 0;
        counter = 0;
      }
    }
  }

  digitalWrite(MR, LOW);
  delay(10);
  digitalWrite(MR, HIGH);
  delay(100);
}

u8 num = 1;
char index = 15;
u16 x = ((u16)digit[0] << 8) | (u16)digit[1];
bool drawing = true;
void loop() {
  if (drawing) {
    digitalWrite(DS, (x >> index) & 1);
    digitalWrite(SH_CP, 1);
    digitalWrite(SH_CP, 0);
    index--;
    if (index < 0) {
      digitalWrite(ST_CP, 1);
      digitalWrite(ST_CP, 0);
      index = 15;
      drawing = false;
      delay(1500);
    }
  } else {
    num = (num + 1) % 100;
    if (g[num] != 0) {
      x = ((u16)digit[num / 10 % 10] << 8) | (u16)digit[num % 10];
      drawing = true;
    }
  }
}

