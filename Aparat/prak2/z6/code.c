

#define DS 4
#define ST_CP 5
#define SH_CP 6
#define MR 7

typedef unsigned char u8;
typedef unsigned short u16;
const u8 digit[] = {
	// G -> A
	0b01111110, // 0
	0b00001100, // 1
	0b10110110, // 2
	0b10011110, // 3
	0b11001100, // 4
	0b11011010, // 5
	0b11111010, // 6
	0b00001110, // 7
	0b11111110, // 8
	0b11011110, // 9
};

bool is_lucky(u8 num) {
	if (num % 2 == 0) return false;
	u8 pos = (num + 1) / 2;
	if (pos % 3 == 0) return false;
	pos -= pos / 3;
	if (pos % 7 == 0) return false;
	pos -= pos / 7;
	if (pos % 9 == 0) return false;
	pos -= pos / 9;
	if (pos % 13 == 0) return false;
	pos -= pos / 13;
	if (pos % 15 == 0) return false;
	pos -= pos / 15;
	if (pos % 21 == 0) return false;
	pos -= pos / 21;
	if (pos % 25 == 0) return false;
	pos -= pos / 25;
	if (pos % 31 == 0) return false;
	pos -= pos / 31;
	return true; 
}

void setup() {
	Serial.begin(9600);
	pinMode(DS, OUTPUT);
	pinMode(ST_CP, OUTPUT);
	pinMode(SH_CP, OUTPUT);
	pinMode(MR, OUTPUT);

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
			delay(1000);
		}
	} else {
		num++;
		if (num > 99) num = 1;
		if (is_lucky(num)) {
			x = ((u16)digit[num / 10 % 10] << 8) | (u16)digit[num % 10];
			drawing = true;
		}
	}
}

