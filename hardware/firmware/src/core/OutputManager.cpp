/**
 * @file OutputManager.cpp
 * @brief Implementation of digital and analog output control
 */

#include "OutputManager.h"
#include "../utils/Logger.h"
#include "../utils/Utils.h"
#include "../subsystems/Buzzer.h"
#include "../subsystems/Safety.h"
#include "../core/Communication.h"
#include "../core/InputManager.h"

// External references
extern InputManager inputManager;
extern Safety safety;
extern Buzzer buzzer;
extern Communication communication;
extern Config config;

// Global instance
OutputManager outputManager;

// DAC object for motor speed control (moved from main)
MCP4725 dac(DAC_ADRESS);

// SPI settings for relay controller
const SPISettings RELAY_CONTROLLER_SPI_SETTINGS(1000000, MSBFIRST, SPI_MODE0);

void OutputManager::init()
{
    // Configure output pins
    pinMode(RELAY_CONTROLLER_SET_OUTPUTS_PIN, OUTPUT);
    digitalWrite(RELAY_CONTROLLER_SET_OUTPUTS_PIN, OUTPUT_OFF);
    pinMode(RELAY_CONTROLLER_ENABLE_PIN, OUTPUT);
    digitalWrite(RELAY_CONTROLLER_ENABLE_PIN, RELAY_CONTROLLER_DISABLED);

    pinMode(ABRIR_CONTROLLER_IN1_PIN, OUTPUT);
    digitalWrite(ABRIR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
    pinMode(ABRIR_CONTROLLER_IN2_PIN, OUTPUT);
    digitalWrite(ABRIR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

    pinMode(COOLING_FAN_CONTROL_PIN, OUTPUT);
    digitalWrite(COOLING_FAN_CONTROL_PIN, COOLING_FAN_OFF);

    pinMode(LED_RED_SIGNAL_PIN, OUTPUT);
    digitalWrite(LED_RED_SIGNAL_PIN, LED_DISABLED);
    pinMode(LED_BLUE_SIGNAL_PIN, OUTPUT);
    digitalWrite(LED_BLUE_SIGNAL_PIN, LED_ENABLED);

    pinMode(FECHAR_CONTROLLER_IN1_PIN, OUTPUT);
    digitalWrite(FECHAR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
    pinMode(FECHAR_CONTROLLER_IN2_PIN, OUTPUT);
    digitalWrite(FECHAR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

    // Configure strobe output
    pinMode(STROBE_INPUT_PIN, OUTPUT);
    digitalWrite(STROBE_INPUT_PIN, OUTPUT_OFF);

    // Initialize strobe state
    strobeState = false;
    strobeMillis = millis();

    // Initialize output state
    outputState.intValue = 0;
    lastOutputState.intValue = 0;

    // Initialize timing
    outputSetMillis = millis();
    refreshOutputMillis = millis();

    // Initialize resistor power control
    resistorPowerState = false;
    resistorPowerValue = 0;
    dutyCycle = 0.0f;
    resistorPowerMillis = millis();

    // Initialize cooling fan control
    coolingFanState = COOLING_FAN_OFF;
    overrideFanState = false;

    // Initialize DAC for motor speed control
    if (dac.isConnected())
    {
        LOG_I(TAG_DAC, "DAC was detected");

        // Set the initial DAC level
        setMotorSpeedLevel(MOTOR_SPEED_LEVEL_OFF);
    }
    else
    {
        LOG_E(TAG_DAC, "no DAC was detected");
    }

    // Turn off all outputs
    setOutputs(OUTPUTS_CONTROL_IMMEDIATE);

    LOG_I(TAG_OUTPUT_MANAGER, "output manager initialized");
}

void OutputManager::processStrobe()
{
    if (millis() > (strobeMillis + STROBE_TOGGLE_INTERVAL))
    {
        // Toggle the strobe input of the microprocessor monitor every 25ms
        digitalWrite(STROBE_INPUT_PIN, strobeState = !strobeState);

        // Reset the strobe toggle timer
        strobeMillis = millis();
    }
}

void OutputManager::setOutputs(bool controlMode)
{
    // Store the control mode in member variable
    this->outputControlMode = controlMode;

    if (millis() > (refreshOutputMillis + OUTPUT_REFRESH_INTERVAL))
    {
        // The output control mode can be either immediate (turn off necessary outputs in case of a warning) or delayed (normal functioning of the program)
        if (this->outputControlMode)
        {
            // The outputs of the shift register are set on a rising edge of this specific pin
            digitalWrite(RELAY_CONTROLLER_SET_OUTPUTS_PIN, LOW);

            // MAX31855 and relay controllers works correctly when SPI MODE 0 due to the change in the polarity signals
            SPI.beginTransaction(RELAY_CONTROLLER_SPI_SETTINGS);
            // Catastrophe state
            //
            // Ventilation will continue while the following scenarios are mantained after the ventilation flag is activated
            //
            // 1 - Half an hour has not yet passed and there is a fault bit active in the thermocouple that makes it impossible to get a temperature reading
            // 2 - Temperature of the thermocouple is above what is considered safe inside the oven
            //
            // The ventilation flag is activated in the following scenarios
            //
            // 1 - An error is detected on a thermocouple by the thermocouple digital converter
            // 2 - The oven over temperature protection input is triggered
            // 3 - Communication with raspberry pi or lavgem board is lost and temperature of the thermocouple is above what is considered safe inside the oven
            if (safety.shouldForceVentilation() && (!bitRead(inputManager.getRealInputs(), ELECTRIC_PROTECTION_BIT)
                                                &&  !bitRead(inputManager.getRealInputs(), MOTOR_OVER_TEMPERATURE_BIT)))
            {
                if (( communication.getOtherBoardStates() & 0b11000000) == DEBOUNCED_DOOR_STATE_CLOSED)
                {
                    outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] = OUTPUT_FORCED_VENTILATION_STATE; // Everything off except vapour output and motor
                }
                else
                {
                    outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] = 0;
                }
                outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] = 0;
            }
            else
            {
                outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] = 0;
                outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] = 0;

                safety.setForceVentilation(false);
            }
            // Check if there is illumination or external buzzer to actuate
            if (bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23], OVEN_ILUMINATION_BIT)
            ||  bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23], BUZZER_EXTERNAL_BIT))
            {
                outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23];
            }
            else
            {
                outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] = 0;
            }
            // Check if there is internal/external buzzer or cooling fan to actuate
            if (!safety.isCommunicationWarningDetected() && (bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA], BUZZER_INTERNAL_BIT)
                                                         ||  bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA], COOLING_FAN_BIT)))
            {
                outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA];

                // The first extra output to control is the internal buzzer
                bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], BUZZER_INTERNAL_BIT ) ? buzzer.play(BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, config.getBuzzerStrength(), config.getBuzzerFrequency()) : buzzer.play(BUZZER_OFF, BUZZER_OFF, BUZZER_OFF, config.getBuzzerStrength(), config.getBuzzerFrequency());

                // The second extra output to control is the cooling fan
                if (!overrideFanState)
                {
                    bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], COOLING_FAN_BIT ) ? coolingFanState = COOLING_FAN_ON : coolingFanState = COOLING_FAN_OFF;

                    digitalWrite(COOLING_FAN_CONTROL_PIN, coolingFanState);
                }
            }
            else if (!safety.isCommunicationWarningDetected() && (!bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA], BUZZER_INTERNAL_BIT)
                                                              ||  !bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA], COOLING_FAN_BIT)))
            {
                outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA];

                // The first extra output to control is the internal buzzer
                bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], BUZZER_INTERNAL_BIT) ? buzzer.play(BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, config.getBuzzerStrength(), config.getBuzzerFrequency()) : buzzer.play(BUZZER_OFF, BUZZER_OFF, BUZZER_OFF, config.getBuzzerStrength(), config.getBuzzerFrequency());

                // The second extra output to control is the cooling fan
                if (!overrideFanState)
                {
                    bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], COOLING_FAN_BIT) ? coolingFanState = COOLING_FAN_ON : coolingFanState = COOLING_FAN_OFF;

                    digitalWrite(COOLING_FAN_CONTROL_PIN, coolingFanState);
                }
            }
            // Transfer the number of bytes that correspond to the number of shift registers present in the board
            SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_16_23]); // Corresponds to the shift register with the outputs 16 to 23
            SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_08_15]); // Corresponds to the shift register with the outputs 08 to 15
            SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07]); // Corresponds to the shift register with the outputs 00 to 07

            // Set the resistor power value to zero
            resistorPowerValue = 0;

            // End the SPI transaction
            SPI.endTransaction();

            // The outputs of the shift register are set on a rising edge of this specific pin
            digitalWrite(RELAY_CONTROLLER_SET_OUTPUTS_PIN, HIGH);

            // Disable the device if no output is actuated
            if ((outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] == 0)
            &&  (outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] == 0)
            &&  (outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] == 0))
            {
                digitalWrite(RELAY_CONTROLLER_ENABLE_PIN, RELAY_CONTROLLER_DISABLED);
            }
            else
            {
                digitalWrite(RELAY_CONTROLLER_ENABLE_PIN, RELAY_CONTROLLER_ENABLED);
            }
        }
        else
        {
            {
                // Only print if the output state has changed
                if ((outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] != this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07])
                ||  (outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] != this->aprovedOutputState[OVEN_OUTPUTS_STATE_08_15])
                ||  (outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] != this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23])
                ||  (outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA] != this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA]))
                {
                    char binary_00_07[9], binary_08_15[9], binary_16_23[9], binary_extra[9];
                    formatByteBinary(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07],    false, binary_00_07);
                    formatByteBinary(this->aprovedOutputState[OVEN_OUTPUTS_STATE_08_15], false, binary_08_15);
                    formatByteBinary(this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23], false, binary_16_23);
                    formatByteBinary(this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA], false, binary_extra);
                    LOG_D(TAG_OUTPUT_MANAGER, "output channel 00-07 - 0b%s | output channel 08-15 - 0b%s | output channel 16-23 - 0b%s | output channel extra - 0b%s", binary_00_07, binary_08_15, binary_16_23, binary_extra);
                }

                bool changeAvailable = true;

                // The first five bits of the byte 0 are actuated in a delayed manner with a small predifined delay between each actuation of the outputs
                if (millis() > (outputSetMillis + OUTPUTS_STATE_CHANGE_DELAY))
                {
                    // Start by the resistor bit first and do motor direction last
                    for (int8_t i = 4; i >= 0; i--)
                    {
                        // Turning off outputs has priority over turning them on
                        //
                        // If a specific output was on previously and now it was requested to be turned off then this is done immediately
                        if ((bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07], i)    == OUTPUT_ON)
                        &&  (bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07], i) == OUTPUT_OFF))
                        {
                            bitWrite(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07], i, OUTPUT_OFF);

                            LOG_D(TAG_OUTPUT_MANAGER, "output number %d will be changed to OFF now", i);

                            outputSetMillis = millis();

                            // An output was turned off so no output can be turned on this timer cycle
                            changeAvailable = false;

                            // Only one output is actuated at a time
                            break;
                        }
                    }
                    // If an action to turn off an output was already executed then no action to turn on an output will be executed until the predifined delay elapses
                    if (changeAvailable)
                    {
                        // Start by the motor direction bit first and do resistor last
                        for (uint8_t i = 0; i <= 4; i++)
                        {
                            if ((bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07], i)    == OUTPUT_OFF)
                            &&  (bitRead(this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07], i) == OUTPUT_ON))
                            {
                                bitWrite(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07], i, OUTPUT_ON);

                                LOG_D(TAG_OUTPUT_MANAGER, "output number %d will be changed to ON now", i);

                                outputSetMillis = millis();

                                // Only one output is actuated at a time
                                break;
                            }
                        }
                    }
                }
                // The last three bits of the output byte 0 can be actuated immediately and all at the same time
                outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] = (outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] & 0b00011111) | (this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07] & 0b11100000);

                // Set the outputs of the remaining shift register acoording to the received data
                outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_08_15];
                outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_16_23];
                outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA] = this->aprovedOutputState[OVEN_OUTPUTS_STATE_EXTRA];

                // Clear the fault in the transmitted global structure that indicates the invalid concurrence of outputs
                bitWrite(safety.setBoardInternalErrors(), FAULT_CONCURRENT_OUTPUTS_BIT, LOW);

                // Set the outputs of the 3 shift registers and then set the state of the extra outputs
                digitalWrite(RELAY_CONTROLLER_SET_OUTPUTS_PIN, LOW);

                // MAX31855 and relay controllers works correctly when SPI MODE 0 due to the change in the polarity signals
                SPI.beginTransaction(RELAY_CONTROLLER_SPI_SETTINGS);

                // Transfer the number of bytes that correspond to the number of shift registers present in the board
                SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_16_23]); // Corresponds to the shift register with the outputs 16 to 23
                SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_08_15]); // Corresponds to the shift register with the outputs 08 to 15
                SPI.transfer(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07]); // Corresponds to the shift register with the outputs 00 to 07

                // End the SPI transaction
                SPI.endTransaction();

                // The outputs of the shift register are set on a rising edge of this specific pin
                digitalWrite(RELAY_CONTROLLER_SET_OUTPUTS_PIN, HIGH);

                // Disable the device if no output is actuated
                if ((outputState.byteArray[OVEN_OUTPUTS_STATE_00_07] == 0)
                &&  (outputState.byteArray[OVEN_OUTPUTS_STATE_08_15] == 0)
                &&  (outputState.byteArray[OVEN_OUTPUTS_STATE_16_23] == 0))
                {
                    digitalWrite(RELAY_CONTROLLER_ENABLE_PIN, RELAY_CONTROLLER_DISABLED);
                }
                else
                {
                    digitalWrite(RELAY_CONTROLLER_ENABLE_PIN, RELAY_CONTROLLER_ENABLED);
                }
                // The first extra output to control is the internal buzzer
                bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], BUZZER_INTERNAL_BIT) ? buzzer.play(BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, BUZZER_ALWAYS_ON, config.getBuzzerStrength(), config.getBuzzerFrequency()) : buzzer.play(BUZZER_OFF, BUZZER_OFF, BUZZER_OFF, config.getBuzzerStrength(), config.getBuzzerFrequency());

                // The second extra output to control is the cooling fan
                if (!overrideFanState)
                {
                    bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_EXTRA], COOLING_FAN_BIT) ? coolingFanState = COOLING_FAN_ON : coolingFanState = COOLING_FAN_OFF;

                    digitalWrite(COOLING_FAN_CONTROL_PIN, coolingFanState);
                }
            }
        }
        refreshOutputMillis = millis();
    }
}

void OutputManager::setMotorSpeedLevel(uint8_t speedLevel)
{
    // Validate the requested motor speed level
    if (speedLevel > MOTOR_SPEED_LEVEL_10)
    {
        speedLevel = MOTOR_SPEED_LEVEL_10;
    }

    // Calculate the target DAC voltage for the requested motor speed level
    float targetDACVoltage = (float)speedLevel / 2.0;

    // Calculate the value to send to the DAC
    uint16_t DACValue = (uint16_t)((targetDACVoltage / 5.0 /*volts*/) * 4095.0);

    // Validate the calculated DAC value
    if (DACValue > 4095)
    {
        DACValue = 4095;
    }
    // Set the DAC value
    int32_t error = dac.setValue(DACValue);

        LOG_D(TAG_DAC, "speed level requested - %u | dac value calculated - %u | dac state - %s", speedLevel, DACValue, (error == MCP4725_OK) ? "OK" : "NOT OK");
}

void OutputManager::setResistorPower()
{
    #ifdef USE_SSR

        if (resistorPowerValue == MINIMUM_DUTY_CYCLE_VALUE)
        {
            digitalWrite(RESISTOR_POWER_CONTROL_PIN, resistorPowerState = RESISTOR_POWER_OFF);
        }
        else if (resistorPowerValue == MAXIMUM_DUTY_CYCLE_VALUE)
        {
            digitalWrite(RESISTOR_POWER_CONTROL_PIN, resistorPowerState = RESISTOR_POWER_ON);
        }
        else if ((resistorPowerValue > MINIMUM_DUTY_CYCLE_VALUE) && (resistorPowerValue < MAXIMUM_DUTY_CYCLE_VALUE))
        {
            if (resistorPowerState && (millis() > (resistorPowerMillis + (uint16_t)dutyCycle)))
            {
                resistorPowerMillis = millis();

                // On part of the duty cycle has finished
                digitalWrite(RESISTOR_POWER_CONTROL_PIN, resistorPowerState = RESISTOR_POWER_OFF);

                dutyCycle = RESISTOR_PWM_PERIOD * ((MAXIMUM_DUTY_CYCLE_VALUE - resistorPowerValue) / MAXIMUM_DUTY_CYCLE_VALUE);

                LOG_D(TAG_OUTPUT_MANAGER, "resistor power duty cycle OFF value is - (int) %d - (float) %d.%02d", (uint16_t)dutyCycle, (int)dutyCycle, (int)((dutyCycle - (int)dutyCycle) * 100));
            }
            else if (!resistorPowerState && (millis() > (resistorPowerMillis + (uint16_t)dutyCycle)))
            {
                resistorPowerMillis = millis();

                // Off part of the duty cycle has finished
                digitalWrite(RESISTOR_POWER_CONTROL_PIN, resistorPowerState = RESISTOR_POWER_ON);

                dutyCycle = RESISTOR_PWM_PERIOD * (resistorPowerValue / MAXIMUM_DUTY_CYCLE_VALUE);

                LOG_D(TAG_OUTPUT_MANAGER, "resistor power duty cycle ON value is - (int) %d - (float) %d.%02d", (uint16_t)dutyCycle, (int)dutyCycle, (int)((dutyCycle - (int)dutyCycle) * 100));
            }
        }
        else
        {
            // Invalido
        }
        if (resistorPowerValue == MINIMUM_DUTY_CYCLE_VALUE)
        {
            bitWrite( this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07] , RESISTOR_BIT , OUTPUT_OFF );
        }
        else
        {
            bitWrite( this->aprovedOutputState[OVEN_OUTPUTS_STATE_00_07] , RESISTOR_BIT , OUTPUT_ON );
        }

    #endif
}

bool OutputManager::getStrobeState() const
{
    return strobeState;
}

bool OutputManager::getCoolingFanState() const
{
    return coolingFanState;
}

void OutputManager::setCoolingFanState(bool state)
{
    coolingFanState = state;
}

bool OutputManager::getOverrideFanState() const
{
    return overrideFanState;
}

void OutputManager::setOverrideFanState(bool state)
{
    overrideFanState = state;
}

byte* OutputManager::getAprovedOutputState()
{
    return aprovedOutputState;
}

void OutputManager::setAprovedOutputState(uint8_t index, byte value)
{
    if (index < REQUESTS_BUFFER_SIZE)
    {
        aprovedOutputState[index] = value;
    }
}

uint8_t OutputManager::getOutputControlMode() const
{
    return outputControlMode;
}

void OutputManager::setOutputControlMode(uint8_t mode)
{
    outputControlMode = mode;
}

outputStateUnion& OutputManager::getOutputState()
{
    return outputState;
}

uint8_t OutputManager::getOutputState(uint8_t byteIndex) const
{
    if (byteIndex < 4)
    {
        return outputState.byteArray[byteIndex];
    }

    return 0;
}

uint8_t OutputManager::getResistorPowerValue() const
{
    return resistorPowerValue;
}

void OutputManager::setResistorPowerValue(uint8_t value)
{
    resistorPowerValue = value;
}
