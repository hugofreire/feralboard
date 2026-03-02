#include "Config.h"
#include "../utils/Logger.h"
#include "../subsystems/Buzzer.h"
#include "../subsystems/Safety.h"

extern void printByteExplicit(byte _byteToPrint, bool _reversed);

Config config;

Config::Config() :
    ovenModel(0),
    buzzerStrength(0),
    buzzerFrequency(0),
    customSlowMotorSpeed(0),
    customFastMotorSpeed(0),
    numberActiveThermocouples(0),
    eepromIntegrity(0),
    eepromError(false)
{
}

void Config::init()
{
    EEPROM.get(EEPROM_INTEGRITY_ADDRESS, eepromIntegrity);

    if (eepromIntegrity == ERROR_EEPROM_VALUE)
    {
        EEPROM.put(EEPROM_INTEGRITY_ADDRESS, OK_EEPROM_VALUE);
        //bitWrite(safety.setBoardInternalErrors(), FAULT_EEPROM_INTERNAL_BIT, HIGH);

        eepromError = true;

        setDefaultValues();
    }
    else
    {
        loadFromEEPROM();
    }
    validateAndSetDefaults();

    debugPrintValues();
}

void Config::loadFromEEPROM()
{
    EEPROM.get(OVEN_MODEL_ADDRESS, ovenModel);
    EEPROM.get(BUZZER_STRENGTH_ADDRESS, buzzerStrength);
    EEPROM.get(BUZZER_FREQUENCY_ADDRESS, buzzerFrequency);
    EEPROM.get(CUSTOM_SLOW_MOTOR_SPEED_ADDRESS, customSlowMotorSpeed);
    EEPROM.get(CUSTOM_FAST_MOTOR_SPEED_ADDRESS, customFastMotorSpeed);
    EEPROM.get(NUMBER_THERMOCOUPLES_ON_BOARD_ADDRESS, numberActiveThermocouples);
}

void Config::setDefaultValues()
{
    buzzerStrength = BUZZER_DEFAULT_STRENGTH;
    EEPROM.put(BUZZER_STRENGTH_ADDRESS, buzzerStrength);

    LOG_W(TAG_EEPROM, "fault detected on saved buzzer strength | value set to default - %u", buzzerStrength);

    customSlowMotorSpeed = DEFAULT_SLOW_MOTOR_SPEED;
    EEPROM.put(CUSTOM_SLOW_MOTOR_SPEED_ADDRESS, customSlowMotorSpeed);

    LOG_W(TAG_EEPROM, "fault detected on custom slow motor speed value | custom slow motor speed value - %u", customSlowMotorSpeed);

    customFastMotorSpeed = DEFAULT_FAST_MOTOR_SPEED;
    EEPROM.put(CUSTOM_FAST_MOTOR_SPEED_ADDRESS, customFastMotorSpeed);

    LOG_W(TAG_EEPROM, "fault detected on custom fast motor speed value | custom fast motor speed value - %u", customFastMotorSpeed);
}

void Config::validateAndSetDefaults()
{
    if (ovenModel > OVEN_TOP_LAVAGEM_ON_ELECTRIC)
    {
        ovenModel = DEFAULT_OVEN_MODEL;
        EEPROM.put(OVEN_MODEL_ADDRESS, ovenModel);
        //bitWrite(safety.setBoardInternalErrors(), FAULT_EEPROM_INTERNAL_BIT, HIGH);
        eepromError = true;

        char ovenModelBinary[9];
        logger.formatByteBinary(ovenModel, false, ovenModelBinary);
        LOG_W(TAG_EEPROM, "fault detected on saved oven model | value set to default - %u (0b%s)", ovenModel, ovenModelBinary);
    }

    if (buzzerFrequency > BUZZER_FREQUENCY_16)
    {
        buzzerFrequency = BUZZER_FREQUENCY_4;
        EEPROM.put(BUZZER_FREQUENCY_ADDRESS, buzzerFrequency);
        //bitWrite(safety.setBoardInternalErrors(), FAULT_EEPROM_INTERNAL_BIT, HIGH);
        eepromError = true;

        LOG_W(TAG_EEPROM, "fault detected on saved buzzer frequency | value set to default - %u", buzzerFrequency);
    }

    if (numberActiveThermocouples > NUMBER_THERMOCOUPLES_ON_BOARD)
    {
        numberActiveThermocouples = DEFAULT_THERMOCOUPLE_AMOUNT;
        EEPROM.put(NUMBER_THERMOCOUPLES_ON_BOARD_ADDRESS, numberActiveThermocouples);
        //bitWrite(safety.setBoardInternalErrors(), FAULT_EEPROM_INTERNAL_BIT, HIGH);
        eepromError = true;

        LOG_W(TAG_EEPROM, "fault detected on saved number of active thermocouples | value set to default - %u", numberActiveThermocouples);
    }
}

void Config::debugPrintValues()
{
    char ovenModelBinary[9];
    logger.formatByteBinary(ovenModel, false, ovenModelBinary);
    LOG_I(TAG_EEPROM, "selected oven model value - %u (0b%s)", ovenModel, ovenModelBinary);
    LOG_I(TAG_EEPROM, "buzzer strength value - %u", buzzerStrength);
    LOG_I(TAG_EEPROM, "buzzer frequency value - %u", buzzerFrequency);
    LOG_I(TAG_EEPROM, "custom slow motor speed value - %u", customSlowMotorSpeed);
    LOG_I(TAG_EEPROM, "custom fast motor speed value - %u", customFastMotorSpeed);
    LOG_I(TAG_EEPROM, "number of active thermocouples - %u", numberActiveThermocouples);
}

uint8_t Config::getOvenModel()
{
    return ovenModel;
}
uint8_t Config::getBuzzerStrength()
{
    return buzzerStrength;
}
uint8_t Config::getBuzzerFrequency()
{
    return buzzerFrequency;
}
uint8_t Config::getCustomSlowMotorSpeed()
{
    return customSlowMotorSpeed;
}
uint8_t Config::getCustomFastMotorSpeed()
{
    return customFastMotorSpeed;
}
uint8_t Config::getNumberActiveThermocouples()
{
    return numberActiveThermocouples;
}

void Config::setOvenModel(uint8_t value)
{
    ovenModel = value;
    EEPROM.put(OVEN_MODEL_ADDRESS, ovenModel);
}
void Config::setBuzzerStrength(uint8_t value)
{
    buzzerStrength = value;
    EEPROM.put(BUZZER_STRENGTH_ADDRESS, buzzerStrength);
}
void Config::setBuzzerFrequency(uint8_t value)
{
    buzzerFrequency = value;
    EEPROM.put(BUZZER_FREQUENCY_ADDRESS, buzzerFrequency);
}
void Config::setCustomSlowMotorSpeed(uint8_t value)
{
    customSlowMotorSpeed = value;
    EEPROM.put(CUSTOM_SLOW_MOTOR_SPEED_ADDRESS, customSlowMotorSpeed);
}
void Config::setCustomFastMotorSpeed(uint8_t value)
{
    customFastMotorSpeed = value;
    EEPROM.put(CUSTOM_FAST_MOTOR_SPEED_ADDRESS, customFastMotorSpeed);
}
void Config::setNumberActiveThermocouples(uint8_t value)
{
    numberActiveThermocouples = value;
    EEPROM.put(NUMBER_THERMOCOUPLES_ON_BOARD_ADDRESS, numberActiveThermocouples);
}

bool Config::hasEEPROMError()
{
    return eepromError;
}

void Config::clearEEPROMError()
{
    eepromError = false;
}

uint8_t Config::getEEPROMIntegrity()
{
    return eepromIntegrity;
}