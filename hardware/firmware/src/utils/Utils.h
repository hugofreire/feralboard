#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <avr/pgmspace.h>

extern const uint8_t crc8_table[256] PROGMEM;

uint8_t calculateChecksum(uint8_t* buffer, uint8_t length);
uint8_t calculateCRC8(uint8_t* buffer, uint8_t length);

void formatByteBinary(uint8_t byte, bool reversed, char* buffer);

#endif