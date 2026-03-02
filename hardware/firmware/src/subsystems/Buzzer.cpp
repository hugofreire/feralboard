#include "Buzzer.h"
#include "../utils/Logger.h"

Buzzer buzzer;

Buzzer::Buzzer() :
    internalState(BUZZER_OFF),
    numberOfBuzzes(BUZZER_OFF),
    strength(BUZZER_DEFAULT_STRENGTH),
    frequency(BUZZER_FREQUENCY_4),
    phase(BUZZER_OFF),
    onDuration(0),
    intervalDuration(0),
    buzzerMillis(0),
    warningBuzzerMillis(0)
{
}

void Buzzer::init()
{
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, OUTPUT_OFF);

    // Load configuration from EEPROM
    strength = config.getBuzzerStrength();
    frequency = config.getBuzzerFrequency();

    // Initialize timing
    buzzerMillis = millis();
    warningBuzzerMillis = millis();

    // Play startup buzzer sequence
    play(SINGLE_EVENT, BUZZER_DURATION_STARTUP, BUZZER_INTERVAL_DEFAULT, strength, frequency);
}

void Buzzer::play(uint8_t number, uint32_t duration, uint32_t interval, uint8_t _strength, uint16_t frequency)
{
    // This function is used to make sure the buzzer requests do not overlap

    // First set the buzzer timers and buzzer strength
    onDuration = duration; intervalDuration = interval; strength = _strength;

    // Buzzer frequency change also changes the tone
    analogWriteFrequency(frequency);

    // Configure the non blocking buzzer routine depending on the buzzer state and number of requested buzzes
    if (number == BUZZER_ALWAYS_ON)
    {
        // The always on buzzer request overtakes any other request even if the buzzer is already on
        internalState = BUZZER_ON; phase = BUZZER_ALWAYS_ON;

        // Start the buzzer request right away to avoid any program blocking function that might come up
        process();
    }
    else if (!internalState && (number != NO_BUZZES))
    {
        // This request will be started but only if the buzzer is not working in order to guarantee that already started requests are not interrupted
        internalState = BUZZER_ON; numberOfBuzzes = number; phase = BUZZER_ON;

        // The buzzer on time will start counting from now
        buzzerMillis = millis();

        // Start the buzzer request right away to avoid any program blocking function that might come up
        process();
    }
    else if (internalState && (number > numberOfBuzzes))
    {
        // If a new buzzer request is received with a higher number of buzzes then the current request in progress will be overriden
        numberOfBuzzes = number;
    }
    else if (number == NO_BUZZES)
    {
        // This is a request to stop the buzzer
        phase = BUZZER_OFF;

        // Start the buzzer request right away to avoid any program blocking function that might come up
        process();
    }
    LOG_D(TAG_BUZZER, "buzzer request received | number of buzzes - %d | buzzer on duration - %ld | buzzer interval duration - %ld | buzzer strength - %d | buzzer frequency - %d", number, duration, interval, _strength, frequency);
}

void Buzzer::process()
{
    // Non blocking buzzing routine
    if (internalState)
    {
        switch (phase)
        {
            case BUZZER_ON:
                {
                    if (millis() > (buzzerMillis + onDuration))
                    {
                        // The time in which the buzzer is on has passed

                        // Switch to the interval between buzzes where the buzzer is off
                        phase = BUZZER_INTERVAL;

                        // The buzzer off time will start counting from now
                        buzzerMillis = millis();
                    }
                    else
                    {
                        analogWrite(BUZZER_PIN, strength);
                    }
                }
                break;
            case BUZZER_ALWAYS_ON:
                {
                    analogWrite(BUZZER_PIN, strength);
                }
                break;
            case BUZZER_INTERVAL:
                {
                    if (numberOfBuzzes == SINGLE_EVENT)
                    {
                        // If only one buzz was requested then the buzzer will be turned off
                        phase = BUZZER_OFF;
                    }
                    else if (millis() > (buzzerMillis + intervalDuration))
                    {
                        // The time in which the buzzer is off has passed

                        // Switch to the duration of time where the buzzer is on
                        numberOfBuzzes--; phase = BUZZER_ON;

                        // The buzzer on time will start counting from now
                        buzzerMillis = millis();
                    }
                    else
                    {
                        analogWrite(BUZZER_PIN, BUZZER_OFF);
                    }
                }
                break;
            case BUZZER_OFF:
                {
                    // Requested number of buzzes is concluded or buzzer requested to turn off

                    // Reset variables
                    internalState = BUZZER_OFF; phase = BUZZER_ON;

                    // And turn the buzzer off
                    analogWrite(BUZZER_PIN, BUZZER_OFF);
                }
                break;
        }
    }
}

void Buzzer::setWarningBuzzerMillis(uint32_t millis)
{
    warningBuzzerMillis = millis;
}

uint32_t Buzzer::getWarningBuzzerMillis()
{
    return warningBuzzerMillis;
}

bool Buzzer::getInternalState()
{
    return internalState;
}