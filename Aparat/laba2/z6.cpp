#include <Arduino.h>
#include "Wire.h"
#include "TroykaLedMatrix.h"
// platformio.ini
// lib_deps = https://github.com/amperka/TroykaLedMatrix

TroykaLedMatrix matrix;

const uint8_t img[3][8] {
  {
    0b01111100,
    0b11111110,
    0b10010010,
    0b11111110,
    0b11010110,
    0b10101010,
    0b11111110,
    0b00000000,
  },

  {
    0b01111100,
    0b11111110,
    0b10010010,
    0b11111110,
    0b10101010,
    0b11010110,
    0b11111110,
    0b00000000,
  },

  {
    0b01111100,
    0b11111110,
    0b10010010,
    0b11111110,
    0b10101010,
    0b10000010,
    0b11111110,
    0b00000000,
  }
};


void setup() {
  Serial.begin(9600);
  matrix.begin();
  matrix.clear();
}

volatile unsigned char index = 0;
void loop() {
  matrix.drawBitmap(img[index]);
  index++;
  if (index > 2) index = 0;
  delay(1000); 
}