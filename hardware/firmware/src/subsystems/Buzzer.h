#ifndef BUZZER_H
#define BUZZER_H

#include "Arduino.h"
#include "../config/Definitions.h"
#include "../config/Config.h"

////////////////////////////////////////////////////////////////////////////////////////////////////

/*
    BUZZER DEFINITIONS
*/
#define BUZZER_OFF                  0x00
#define BUZZER_ON                   0x01
#define BUZZER_INTERVAL             0x02
#define BUZZER_ALWAYS_ON            0xFF

#define BUZZER_DEFAULT_STRENGTH     255

#define BUZZER_DURATION_STARTUP     1000
#define BUZZER_DURATION_DEFAULT     500
#define BUZZER_DURATION_WARNING     1000

#define BUZZER_INTERVAL_STARTUP     1000
#define BUZZER_INTERVAL_DEFAULT     500
#define BUZZER_INTERVAL_WARNING     500

#define NO_BUZZES                   0
#define SINGLE_EVENT                1
#define DOUBLE_EVENT                2
#define TRIPLE_EVENT                3
#define QUADRUPLE_EVENT             4
#define QUINTUPLE_EVENT             5

#define BUZZER_FREQUENCY_1          1
#define BUZZER_FREQUENCY_4          4
#define BUZZER_FREQUENCY_8          8
#define BUZZER_FREQUENCY_16         16
#define BUZZER_FREQUENCY_32         32
#define BUZZER_FREQUENCY_64         64

////////////////////////////////////////////////////////////////////////////////////////////////////

class Buzzer {
public:
    Buzzer();

    void init();
    void process();
    void play(uint8_t numberOfBuzzes, uint32_t duration, uint32_t interval, uint8_t strength, uint16_t frequency);

    // Warning system integration
    void setWarningBuzzerMillis(uint32_t millis);
    uint32_t getWarningBuzzerMillis();

    // State queries
    bool getInternalState();

private:
    // Internal state variables
    bool internalState;
    uint8_t numberOfBuzzes;
    uint8_t strength;
    uint16_t frequency;
    uint8_t phase;

    // Timing variables
    uint32_t onDuration;
    uint32_t intervalDuration;
    uint32_t buzzerMillis;
    uint32_t warningBuzzerMillis;
};

extern Buzzer buzzer;

#endif