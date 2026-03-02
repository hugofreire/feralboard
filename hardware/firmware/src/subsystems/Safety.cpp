#include "Safety.h"
#include "../utils/Logger.h"
#include "../subsystems/Buzzer.h"
#include "../config/Config.h"
#include "../core/Communication.h"
#include "../core/Temperature.h"
#include "../core/OutputManager.h"

// External function declarations

// External variable declarations
extern temperatureValueTCUnion thermocoupleMeasurements[NUMBER_THERMOCOUPLES_ON_BOARD];
extern OutputManager outputManager;
extern Config config;

// Global instance
Safety safety;

Safety::Safety() :
    communicationWarningDetected(false),
    enableWarningDetection(false),
    communicationWarningLavagemDetected(false),
    enableWarningLavagemDetection(false),
    communicationWarningMillis(0),
    communicationWarningLavagemMillis(0),
    warningBuzzerMillis(0),
    ventilationErrorMillis(0),
    resistorMonitoringActive(false),
    wasAbove50(false),
    resistorStartTemperature(0.0f),
    resistorOnStartTime(0),
    lastResistorCheckTime(0),
    tempErrorDetected(false),
    forceVentilation(false),
    forceVentilationMillis(0)
{
}

void Safety::init()
{
    communicationWarningMillis = millis();
    communicationWarningLavagemMillis = millis();
    warningBuzzerMillis = millis();
    ventilationErrorMillis = 0;
    forceVentilationMillis = 0;

    resistorMonitoringActive = false;
    wasAbove50 = false;
    resistorStartTemperature = 0.0f;
    resistorOnStartTime = 0;
    lastResistorCheckTime = 0;

    communicationWarningDetected = false;
    enableWarningDetection = false;
    communicationWarningLavagemDetected = false;
    enableWarningLavagemDetection = false;
    tempErrorDetected = false;
    forceVentilation = false;
}

void Safety::process()
{
    checkCommunicationTimeouts();

    processWarnings();

    checkVentilationError();

    checkResistorError();
}

void Safety::resetExtraSerialTimer()
{
    // Called when a valid message is received from EXTRA serial
    communicationWarningMillis = millis(); communicationWarningDetected = false; enableWarningDetection = true;
}

void Safety::resetRS485SerialTimer()
{
    // Called when a valid message is received from RS485 serial (Lavagem)
    communicationWarningLavagemMillis = millis(); communicationWarningLavagemDetected = false; enableWarningLavagemDetection = true;
}

void Safety::checkCommunicationTimeouts()
{
    // Simplified: communication timeouts disabled, board holds last output state indefinitely
}

void Safety::processWarnings()
{
    // Communication warning detected
    if (communicationWarningDetected && (millis() > (getWarningBuzzerMillis() + WARNING_BUZZER_INTERVAL)))
    {
        // Reset the warning timer
        setWarningBuzzerMillis(millis());

        // Play the buzzer
        buzzer.play(TRIPLE_EVENT, BUZZER_DURATION_WARNING, BUZZER_INTERVAL_WARNING, config.getBuzzerStrength(), config.getBuzzerFrequency());
    }
}

void Safety::checkVentilationError()
{
    if (  bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], RESISTOR_BIT)
    && ((!bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], DIRECTION_1_BIT)
    &&   !bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], DIRECTION_2_BIT))
    ||  (!bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], VELOCIDADE_1_BIT)
    &&   !bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], VELOCIDADE_2_BIT))))
    {
        if (ventilationErrorMillis == 0)
        {
            ventilationErrorMillis = millis();
        }
        else if (millis() > (ventilationErrorMillis + RESISTOR_ON_VENTILATION_OFF_ERROR_DELAY))
        {
            // Force ventilation on a single direction
            byte currentState = outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07];

            outputManager.setAprovedOutputState(OVEN_OUTPUTS_STATE_00_07, currentState | 0b00001001);

            LOG_W(TAG_WARNING, "resistor is on but no order was given to turn on ventilation in 10 seconds | forcing ventilation");
        }
    }
    else
    {
        ventilationErrorMillis = 0;
    }
}

bool Safety::shouldForceVentilation()
{
    // Simplified: forced ventilation disabled
    return false;
}

void Safety::setForceVentilation(bool enable)
{
    // Simplified: forced ventilation disabled, always stays false
    forceVentilation = false;
    forceVentilationMillis = 0;
}

void Safety::setTempErrorDetected(bool detected)
{
    tempErrorDetected = detected;
}

void Safety::updateFaultFlags()
{
    // Simplified: no internal error flags, error byte 23 always 0x00
    this->boardInternalErrors = 0x00;
}

bool Safety::isCommunicationWarningDetected() const
{
    return communicationWarningDetected;
}

bool Safety::isCommunicationLavagemWarningDetected() const
{
    return communicationWarningLavagemDetected;
}

bool Safety::isTempErrorDetected() const
{
    return tempErrorDetected;
}

bool Safety::isForceVentilationActive() const
{
    return forceVentilation;
}

uint32_t Safety::getForceVentilationMillis() const
{
    return forceVentilationMillis;
}

uint32_t Safety::getWarningBuzzerMillis() const
{
    return warningBuzzerMillis;
}

void Safety::setWarningBuzzerMillis(uint32_t millis)
{
    warningBuzzerMillis = millis;
}

void Safety::resetCommunicationWarning()
{
    communicationWarningMillis = millis(); setWarningBuzzerMillis(0); communicationWarningDetected = true; enableWarningDetection = false;
}

void Safety::resetLavagemWarning()
{
    communicationWarningLavagemMillis = millis(); setWarningBuzzerMillis(0); communicationWarningLavagemDetected = true; enableWarningLavagemDetection = false;
}

uint8_t Safety::getBoardInternalErrors() const
{
    return boardInternalErrors;
}

uint8_t& Safety::setBoardInternalErrors()
{
    return boardInternalErrors;
}

void Safety::checkResistorError()
{
    // Check every second only
    if ((millis() - lastResistorCheckTime) < 1000)
    {
        return;
    }

    lastResistorCheckTime = millis();

    // Read current resistor state
    bool resistorIsOn = bitRead(outputManager.getAprovedOutputState()[OVEN_OUTPUTS_STATE_00_07], RESISTOR_BIT);

    // Get current temperature
    float currentTemperature = thermocoupleMeasurements[temperature.getActiveChannel()].floatValue;

    // Only perform monitoring if temperature is above 50°C
    if (currentTemperature <= RESISTOR_ON_ERROR_TEMPERATURE)
    {
        // Temperature too low so reset monitoring if it was active
        if (resistorMonitoringActive)
        {
            resistorMonitoringActive = false;

            char tempStr1[10]; dtostrf(RESISTOR_ON_ERROR_TEMPERATURE, 0, 0, tempStr1);
            char tempStr2[10]; dtostrf(currentTemperature,            0, 2, tempStr2);

            LOG_I(TAG_RESISTOR_MONITOR, "temperature below %s°C (%s°C) | resistor error monitoring disabled", tempStr1, tempStr2);
        }

        return;
    }

    if (resistorIsOn)
    {
        if (!resistorMonitoringActive)
        {
            // Resistor just turned on or temperature just crossed 50°C so we start monitoring
            resistorMonitoringActive = true; resistorOnStartTime = millis();

            resistorStartTemperature = currentTemperature;

            char tempStr3[10]; dtostrf(resistorStartTemperature, 0, 2, tempStr3);

            LOG_I(TAG_RESISTOR_MONITOR, "starting resistor performance monitoring | start temp: %s°C", tempStr3);
        }
        else
        {
            // Resistor is on and we are monitoring
            uint32_t passedTime = millis() - resistorOnStartTime;

            // Check if 2 minutes (120000ms) have passed
            if (passedTime >= RESISTOR_ON_TEMEPERATURE_ERROR_DELAY)
            {
                float temperatureIncrease = currentTemperature - resistorStartTemperature;

                if (temperatureIncrease < RESISTOR_ON_THRESHOLD_TEMPERATURE)
                {
                    // Temperature did not increase by 2°C in 2 minutes so we trigger the error
                    bitWrite(this->boardInternalErrors, FAULT_RESISTOR_PROBLEM_BIT, HIGH);

                    char tempStr4[10]; dtostrf(temperatureIncrease,               0, 2, tempStr4);
                    char tempStr5[10]; dtostrf(RESISTOR_ON_THRESHOLD_TEMPERATURE, 0, 1, tempStr5);
                    char tempStr6[10]; dtostrf(resistorStartTemperature,          0, 2, tempStr6);
                    char tempStr7[10]; dtostrf(currentTemperature,                0, 2, tempStr7);

                    LOG_W(TAG_WARNING, "resistor fault detected | temperature only increased %s°C in 2 minutes (expected >= %s°C) | start: %s°C | current: %s°C", tempStr4, tempStr5, tempStr6, tempStr7);

                    // Reset monitoring to avoid repeated errors
                    resistorMonitoringActive = false;
                }
                else
                {
                    // Temperature increased properly so reset monitoring for next cycle
                    resistorStartTemperature = currentTemperature; resistorOnStartTime = millis();

                    char tempStr8[10]; dtostrf(temperatureIncrease, 0, 2, tempStr8);

                    LOG_I(TAG_RESISTOR_MONITOR, "resistor performance OK | temperature increased %s°C in 2 minutes | resetting monitor", tempStr8);
                }
            }
        }
    }
    else
    {
        // Resistor is off
        if (resistorMonitoringActive)
        {
            // Resistor was just turned off so reset monitoring
            resistorMonitoringActive = false;

            uint32_t monitoredTime = millis() - resistorOnStartTime;

            float monitoredSeconds = monitoredTime / 1000.0f;

            float temperatureChange = currentTemperature - resistorStartTemperature;

            char tempStr9[10];  dtostrf(monitoredSeconds,  0, 1, tempStr9);
            char tempStr10[10]; dtostrf(temperatureChange, 0, 2, tempStr10);

            LOG_I(TAG_RESISTOR_MONITOR, "resistor turned off | stopping monitoring | duration: %ss | temperature change: %s°C", tempStr9, tempStr10);
        }
    }
}