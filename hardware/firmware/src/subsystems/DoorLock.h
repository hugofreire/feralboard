/**
 * @file DoorLock.h
 * @brief Door lock state machine and motor control
 *
 * Responsibilities:
 * - Electric lock state detection and control
 * - Manual lock position sensing
 * - Motor speed and direction control
 * - Door repositioning sequences
 * - Lock fault detection and recovery
 * - State transition validation
 * - Coordinates with InputManager and OutputManager
 */

#ifndef DOORLOCK_H
#define DOORLOCK_H

#include <Arduino.h>

class DoorLock
{
public:
    // Initialization
    void init();

    // Main processing
    void process();

    // State getters
    uint8_t getDoorState() const;
    uint8_t getDoorPhase() const;
    bool isFaultyLock() const;
    bool isSecondTRy() const;
    bool isDoorReposition() const;
    uint8_t getMotorState() const;
    uint8_t getMotorSpeed() const;

    // State setters
    void setFaultyLock(bool state);
    void setSecondTry(bool state);
    void setDoorReposition(bool state);
    void setDoorState(uint8_t state);
    void setDoorStateCounter(uint8_t counter);
    void setDoorPhase(uint8_t phase);
    void setDoorPhaseMillis(uint32_t millis);
    void setDoorFaultMillis(uint32_t millis);

    // Motor control (called from Communication module for door commands)
    void motorProcess(uint8_t direction, uint8_t speed);

    // Motor state update for otherBoardStates reporting
    void updateMotorStates(byte& otherBoardStates);

private:
    // Door lock state variables
    bool doorReposition;
    bool faultyLock;
    bool secondTry;
    uint8_t customSlowMotorSpeed;
    uint8_t customFastMotorSpeed;
    uint8_t motorState;
    uint8_t motorSpeed;
    uint8_t doorState;
    uint8_t doorStateCounter;
    uint8_t doorPhase;
    uint8_t repositionPhase;
    uint8_t repositionCounter;
    uint32_t doorReadMillis;
    uint32_t doorPhaseMillis;
    uint32_t doorFaultMillis;
    uint32_t repositionPhaseMillis;
    uint32_t secondTryMillis;
    uint32_t debugDoorStateMillis;

    // Helper functions
    void processElectricLock();
    void processManualLock();
};

// Global instance
extern DoorLock doorLock;

#endif // DOORLOCK_H
