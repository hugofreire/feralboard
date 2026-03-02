/**
 * @file OutputManager.h
 * @brief Digital and analog output control system
 *
 * Responsibilities:
 * - Digital output state management and control (shift registers)
 * - PWM output generation for motor speed control (DAC)
 * - Resistor power control via SSR with PWM
 * - Output state validation and safety checks
 * - Relay and solenoid control
 * - Output timing and sequencing (delayed actuation)
 * - Strobe signal generation for microprocessor monitor
 * - Cooling fan control
 * - Internal buzzer control coordination
 */

#ifndef OUTPUT_MANAGER_H
#define OUTPUT_MANAGER_H

#include <Arduino.h>
#include "../config/Definitions.h"

class OutputManager
{
public:
    // Initialization
    void init();

    // Main processing functions
    void processStrobe();
    void setOutputs(bool outputControlMode);
    void setMotorSpeedLevel(uint8_t speedLevel);
    void setResistorPower();

    // State getters
    bool getStrobeState() const;
    outputStateUnion& getOutputState();
    uint8_t getOutputState(uint8_t byteIndex) const;
    uint8_t getResistorPowerValue() const;

    // State setters
    void setResistorPowerValue(uint8_t value);

    // Cooling fan control
    bool getCoolingFanState() const;
    void setCoolingFanState(bool state);
    bool getOverrideFanState() const;
    void setOverrideFanState(bool state);

    // Approved output state access
    byte* getAprovedOutputState();
    void setAprovedOutputState(uint8_t index, byte value);

    // Output control mode
    uint8_t getOutputControlMode() const;
    void setOutputControlMode(uint8_t mode);

private:
    // Strobe management
    bool strobeState;
    uint32_t strobeMillis;

    // Output state storage
    outputStateUnion outputState;
    outputStateUnion lastOutputState;

    // Output timing
    uint32_t outputSetMillis;
    uint32_t refreshOutputMillis;

    // Resistor power control (SSR with PWM)
    bool resistorPowerState;
    uint8_t resistorPowerValue;
    float dutyCycle;
    uint32_t resistorPowerMillis;

    // Cooling fan control
    bool coolingFanState;
    bool overrideFanState;

    // Approved output state buffer (from communication)
    byte aprovedOutputState[REQUESTS_BUFFER_SIZE];

    // Output control mode
    uint8_t outputControlMode;
};

// Global instance
extern OutputManager outputManager;

#endif // OUTPUT_MANAGER_H
