#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <EEPROM.h>
#include "Definitions.h"

////////////////////////////////////////////////////////////////////////////////////////////////////

/*
    EEPROM DEFINITIONS

    ATMEGA4809 EEPROM ADDRESS   0   TO 255 (0x000 - 0x0FF)
    ATMEGA4809 USERROW ADDRESS  256 TO 319 (0x100 - 0x13F)
*/
#define OVEN_MODEL_ADDRESS                                          0x100
#define BUZZER_STRENGTH_ADDRESS                                     0x103
#define BUZZER_FREQUENCY_ADDRESS                                    0x104
#define CUSTOM_SLOW_MOTOR_SPEED_ADDRESS                             0x105
#define CUSTOM_FAST_MOTOR_SPEED_ADDRESS                             0x106
#define NUMBER_THERMOCOUPLES_ON_BOARD_ADDRESS                       0x107
#define DETERGENT_PERCENTAGE_AMOUNT_ADDRESS                         0x108

#define EEPROM_INTEGRITY_ADDRESS                                    0x13F

#define OK_EEPROM_VALUE                                             69
#define ERROR_EEPROM_VALUE                                          255

////////////////////////////////////////////////////////////////////////////////////////////////////

class Config {
public:
    Config();

    void init();
    void loadFromEEPROM();
    void validateAndSetDefaults();

    uint8_t getOvenModel();
    uint8_t getBuzzerStrength();
    uint8_t getBuzzerFrequency();
    uint8_t getCustomSlowMotorSpeed();
    uint8_t getCustomFastMotorSpeed();
    uint8_t getNumberActiveThermocouples();

    void setOvenModel(uint8_t value);
    void setBuzzerStrength(uint8_t value);
    void setBuzzerFrequency(uint8_t value);
    void setCustomSlowMotorSpeed(uint8_t value);
    void setCustomFastMotorSpeed(uint8_t value);
    void setNumberActiveThermocouples(uint8_t value);

    bool hasEEPROMError();
    void clearEEPROMError();

    // EEPROM integrity
    uint8_t getEEPROMIntegrity();

private:
    uint8_t ovenModel;
    uint8_t buzzerStrength;
    uint8_t buzzerFrequency;
    uint8_t customSlowMotorSpeed;
    uint8_t customFastMotorSpeed;
    uint8_t numberActiveThermocouples;
    uint8_t eepromIntegrity;
    bool eepromError;

    void setDefaultValues();
    void debugPrintValues();
};

extern Config config;

#endif