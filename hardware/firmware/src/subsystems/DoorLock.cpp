/**
 * @file DoorLock.cpp
 * @brief Implementation of door lock state machine and motor control
 *
 * This module manages the complex state machine for electric door locks
 * and manual door position sensing. It coordinates with InputManager for
 * door sensor state reading and directly controls motor drivers.
 */

#include "DoorLock.h"
#include "../config/Definitions.h"
#include "../config/Config.h"
#include "../core/InputManager.h"
#include "../core/Communication.h"
#include "../utils/Logger.h"
#include "../utils/Utils.h"

// Global instance definition
DoorLock doorLock;

// External references
extern InputManager inputManager;
extern Communication communication;
extern Config config;

void DoorLock::init()
{
    // Initialize door lock state variables
    doorReposition = false;
    faultyLock = false;
    secondTry = false;
    motorState = MOTORS_OFF;
    motorSpeed = MOTORS_OFF;
    doorState = MASK_DOOR_UNKNOWN_ELECTRIC;
    doorStateCounter = 0;
    doorPhase = DOOR_UNKNOWN_STATE_ELECTRIC;
    repositionPhase = 0;
    repositionCounter = 0;

    // Get motor speeds from configuration
    customSlowMotorSpeed = config.getCustomSlowMotorSpeed();
    customFastMotorSpeed = config.getCustomFastMotorSpeed();

    // Initialize timers
    doorReadMillis = millis();
    setDoorPhaseMillis(millis());
    setDoorFaultMillis(millis());
    repositionPhaseMillis = millis();
    debugDoorStateMillis = millis();
}

void DoorLock::process()
{
    // The type of lock is defined in the first bit of the oven model
    if (bitRead(config.getOvenModel(), OVEN_MODEL_LOCK_TYPE_BIT) == LOCK_TYPE_ELECTRIC)
    {
        processElectricLock();
    }

    // The type of lock is defined in the first bit of the oven model
    if (bitRead(config.getOvenModel(), OVEN_MODEL_LOCK_TYPE_BIT) == LOCK_TYPE_MANUAL)
    {
        processManualLock();
    }
}

uint8_t DoorLock::getDoorState() const
{
    return doorState;
}

uint8_t DoorLock::getDoorPhase() const
{
    return doorPhase;
}

bool DoorLock::isFaultyLock() const
{
    return faultyLock;
}

bool DoorLock::isSecondTRy() const
{
    return secondTry;
}

bool DoorLock::isDoorReposition() const
{
    return doorReposition;
}

uint8_t DoorLock::getMotorState() const
{
    return motorState;
}

uint8_t DoorLock::getMotorSpeed() const
{
    return motorSpeed;
}

void DoorLock::setFaultyLock(bool state)
{
    faultyLock = state;
}

void DoorLock::setSecondTry(bool state)
{
    secondTry = state;
}

void DoorLock::setDoorReposition(bool state)
{
    doorReposition = state;
}

void DoorLock::setDoorState(uint8_t state)
{
    doorState = state;
}

void DoorLock::setDoorStateCounter(uint8_t counter)
{
    doorStateCounter = counter;
}

void DoorLock::setDoorPhase(uint8_t phase)
{
    doorPhase = phase;
}

void DoorLock::setDoorPhaseMillis(uint32_t millis)
{
    doorPhaseMillis = millis;
}

void DoorLock::setDoorFaultMillis(uint32_t millis)
{
    doorFaultMillis = millis;
}

void DoorLock::updateMotorStates(byte& otherBoardStates)
{
    // Motor states are already updated in motorProcess() function

    // This function is kept for future use if needed
}

void DoorLock::processElectricLock()
{
    // Get the door state from the inputs
    // The inputs that need to be checked to get the door state depend on the model of the oven
    // The type of lock is defined in the first bit of the oven model
    if (millis() > (doorReadMillis + DELAY_BETWEEN_DOOR_READINGS))
    {
        // Use a delay between the processing of the electric lock inputs
        doorReadMillis = millis();

        // Process just the state of the door inputs
        if (doorState != (inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK))
        {
            uint8_t _doorState = inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK;

            switch (_doorState)
            {
                case MASK_DOOR_OPEN_ELECTRIC:
                    {
                        doorState = _doorState;

                        // Stop any motor that might be working when the door is detected to be open
                        motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                        // Set the door phase indicating that the door is now open
                        doorPhase = DOOR_OPEN_ELECTRIC;

                        // A new valid state was detected which resets the counter responsible to detect unrecoginizable states on the electric lock
                        doorStateCounter = 0;

                        // Unblock all electric lock operations
                        faultyLock = false; secondTry = false;

                        char binary_door_state[9];
                        formatByteBinary(_doorState, false, binary_door_state);
                        LOG_I(TAG_DOOR_STATE, "door state changed to OPEN (0b%s)", binary_door_state);
                    }
                    break;
                case MASK_DOOR_INTERMEDIATE_ELECTRIC:
                    {
                        // Situation 1 - a manual attempt was made to close the door but not enough force was applied resulting in the door to be detected as being in the intermediate state and the factory mode is off
                        // Situation 2 - the microcontroller was just initiated (door was in an unknown state) and then the door is then detected to be in an intermediate state and the factory mode is off
                        // Situation 3 - the panel is in factory mode which means open and close requests (even if the door is in the intermediate state) are only done per user request from the factory settings page
                        doorState = _doorState;

                        // Situation 1 and 2
                        if (!faultyLock && !doorReposition && !communication.isFactoryMode() && ((doorPhase == DOOR_OPEN_ELECTRIC) || (doorPhase == DOOR_ALREADY_CLOSED_ELECTRIC) || (doorPhase == DOOR_UNKNOWN_STATE_ELECTRIC)))
                        {
                            motorProcess(DOOR_CLOSING_ELECTRIC, customFastMotorSpeed);

                            // The closing motor was started which means the door is in a closing phase
                            doorPhase = DOOR_CLOSING_ELECTRIC;

                            // Reset the timer that will check the elapsed time during door closing
                            setDoorPhaseMillis(millis());
                        }

                        // A new valid state was detected which resets the counter responsible to detect unrecoginizable states on the electric lock
                        doorStateCounter = 0;

                        char binary_door_state[9];
                        formatByteBinary(_doorState, false, binary_door_state);
                        LOG_I(TAG_DOOR_STATE, "door state changed to INTERMEDIATE (0b%s)", binary_door_state);
                    }
                    break;
                case MASK_DOOR_CLOSED_ELECTRIC:
                    {
                        // Situation 1 - the microcontroller was just initiated and the door is detected as being closed
                        // Situation 2 - the door was closed manually with enough force to lock it and for it to be detected as being closed
                        // Situation 3 - the closing motor was previously engaged and the door is now detected as being closed
                        doorState = _doorState;

                        // Situation 1
                        if (!faultyLock && !doorReposition && !communication.isFactoryMode() && (doorPhase == DOOR_UNKNOWN_STATE_ELECTRIC))
                        {
                            motorProcess(DOOR_CLOSING_ELECTRIC, customSlowMotorSpeed);

                            // The door is fully closed
                            doorPhase = DOOR_ALREADY_CLOSED_ELECTRIC;

                            // Reset the variable responsible to make sure the closing motor just works for a predifined amount of time
                            setDoorPhaseMillis(millis());
                        }

                        // Situation 2
                        if (!faultyLock && !doorReposition && !communication.isFactoryMode() && (doorPhase == DOOR_OPEN_ELECTRIC))
                        {
                            motorProcess(DOOR_CLOSING_ELECTRIC, customSlowMotorSpeed);

                            // The door is fully closed
                            doorPhase = DOOR_ALREADY_CLOSED_ELECTRIC;

                            // Reset the variable responsible to make sure the closing motor just works for a predifined amount of time
                            setDoorPhaseMillis(millis());
                        }

                        // Situation 3
                        if (!faultyLock && !doorReposition && (doorPhase == DOOR_CLOSING_ELECTRIC))
                        {
                            motorProcess(DOOR_CLOSING_ELECTRIC, customSlowMotorSpeed);

                            // The door is fully closed
                            doorPhase = DOOR_ALREADY_CLOSED_ELECTRIC;

                            // Reset the variable responsible to make sure the closing motor just works for a predifined amount of time
                            setDoorPhaseMillis(millis());
                        }

                        // A new valid state was detected which resets the counter responsible to detect unrecoginizable states on the electric lock
                        doorStateCounter = 0;

                        char binary_door_state[9];
                        formatByteBinary(_doorState, false, binary_door_state);
                        LOG_I(TAG_DOOR_STATE, "door state changed to CLOSED (0b%s)", binary_door_state);
                    }
                    break;
                default:
                    {
                        if (!faultyLock && !doorReposition)
                        {
                            // If the door state is not detected after a predifined amount of times then the door reposition is automatically started
                            if (doorStateCounter > LOCK_REPOSITION_TRIGGER)
                            {
                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                                // Start the door reposition
                                doorReposition = true;

                                // Place the door into an unknown state
                                doorPhase = DOOR_UNKNOWN_STATE_ELECTRIC;

                                // Reset the door state counter to avoid immediately starting the door reposition again if a future door blocking ocurrs
                                doorStateCounter = 0;

                                // Reset the timer that will check the elapsed time during the door reposition
                                setDoorFaultMillis(millis());

                                LOG_W(TAG_DOOR_STATE, "lock state is unrecognizable | starting the electric lock reposition");
                            }
                            else
                            {
                                doorStateCounter++;
                            }

                            if (millis() > (debugDoorStateMillis + SERIAL_DOOR_STATE_PRINT_DELAY))
                            {
                                debugDoorStateMillis = millis();

                                // Print the door other state every 5 seconds
                                char binary_door_state[9];
                                formatByteBinary(_doorState, false, binary_door_state);
                                LOG_W(TAG_DOOR_STATE, "door state changed to OTHER (0b%s)", binary_door_state);
                            }
                        }
                    }
                    break;
            }
        }
    }
    if (doorReposition)
    {
        // If too much time goes by without the lock process being able to conclude then trigger an error
        if (millis() > (doorFaultMillis + (DOOR_MOVEMENT_ERROR_DELAY * 5 /* 15 seconds */ )))
        {
            motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

            // Door reposition is stopped
            doorReposition = false;

            // Place the door into an unknown state
            doorPhase = DOOR_ERROR_STATE_ELECTRIC;

            // Block some electric lock operations
            faultyLock = true;

            // Reset the auto reposition sequence back to the first phase
            repositionPhase = 0x00;

            // Second try to reposition the lock will start in a bit
            secondTryMillis = millis();

            secondTry ? (TAG_DOOR_STATE, "fault detected on electric lock for the second try") : (TAG_DOOR_STATE, "fault detected on electric lock");
        }
        else
        {
            switch (repositionPhase)
            {
                case 0x00:
                    {
                        // First phase of the auto reposition sequence will detect which motor should be actuated first
                        repositionPhaseMillis = millis(); repositionCounter = 0; repositionCounter++;

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10000000) == 0b10000000)
                        {
                            repositionPhase = 0x01;

                            LOG_W(TAG_DOOR_STATE, "lock reposition start | traction switch NOT FOUND");

                            motorProcess(DOOR_CLOSING_ELECTRIC, customSlowMotorSpeed);
                        }
                        else if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00100000) == 0b00100000)
                        {
                            repositionPhase = 0x03;

                            LOG_W(TAG_DOOR_STATE, "lock reposition start | locking switch 1 NOT FOUND");

                            motorProcess(DOOR_OPENING_ELECTRIC, customSlowMotorSpeed);
                        }
                        else if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00010000) == 0b00010000)
                        {
                            repositionPhase = 0x05;

                            LOG_W(TAG_DOOR_STATE, "lock reposition start | locked switch NOT FOUND");

                            motorProcess(DOOR_OPENING_ELECTRIC, customSlowMotorSpeed);
                        }
                    }
                    break;
                case 0x01:
                    {
                        // If after a predifined amount of time the traction switch is not found then start the closing motor in the reverse direction
                        if (millis() > (repositionPhaseMillis + (DOOR_REPOSITION_CLOSING_DELAY * repositionCounter)))
                        {
                            // Auto reposition sequence switches to moving the closing motor in the reverse direction
                            repositionPhase = 0x02; repositionPhaseMillis = millis();

                            LOG_W(TAG_DOOR_STATE, "traction switch NOT FOUND 1 - %d", DOOR_REPOSITION_CLOSING_DELAY * repositionCounter);

                            motorProcess(DOOR_CLOSING_REVERSE_ELECTRIC, customSlowMotorSpeed);
                        }

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10000000) == 0b00000000)
                        {
                            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10010000) == 0b00010000)
                            {
                                // End the auto reposition sequence
                                repositionPhase = 0x00; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "traction switch FOUND 1 and locked switch BAD");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                            // When the traction switch is found when the closing motor is moving in the normal direction and the locking switch 1 is in the correct position then end the lock reposition sequence
                            else if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00100000) == 0b00000000)
                            {
                                // End the auto reposition sequence
                                repositionPhase = 0x06; repositionPhaseMillis = millis();

                                LOG_I(TAG_DOOR_STATE, "traction switch FOUND 1 and locking switch 1 OK");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                            // When the traction switch is found when the closing motor is moving in the normal direction and the locking switch 1 is not in the correct position then start the opening motor in the normal direction
                            else
                            {
                                // Auto reposition sequence switches to moving the opening motor in the normal direction
                                repositionPhase = 0x03; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "traction switch FOUND 1 and locking switch 1 BAD");

                                motorProcess(DOOR_OPENING_ELECTRIC, customSlowMotorSpeed);
                            }
                        }
                    }
                    break;
                case 0x02:
                    {
                        // If after a predifined amount of tries the traction switch is still not found then start the opening motor in the normal direction
                        if (millis() > (repositionPhaseMillis + (DOOR_REPOSITION_CLOSING_DELAY * repositionCounter)))
                        {
                            if (repositionCounter > DOOR_REPOSITION_CLOSING_TRIES)
                            {
                                // Auto reposition sequence switches to moving the opening motor in the normal direction
                                repositionPhase = 0x03; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "traction switch NOT FOUND 3 - %d", DOOR_REPOSITION_CLOSING_DELAY * repositionCounter);

                                motorProcess(DOOR_OPENING_ELECTRIC, customSlowMotorSpeed);
                            }
                            else
                            {
                                // Auto reposition sequence switches to moving the closing motor in the normal direction for more time
                                repositionPhase = 0x01; repositionPhaseMillis = millis(); repositionCounter++;

                                LOG_W(TAG_DOOR_STATE, "traction switch NOT FOUND 2 - %d", DOOR_REPOSITION_CLOSING_DELAY * repositionCounter);

                                motorProcess(DOOR_CLOSING_ELECTRIC, customSlowMotorSpeed);
                            }
                        }

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10000000) == 0b00000000)
                        {
                            // When the traction switch is found when the closing motor is moving in the reverse direction and the locking switch 1 is in the correct position then end the lock reposition sequence
                            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00100000) == 0b00000000)
                            {
                                // End the auto reposition sequence
                                repositionPhase = 0x06; repositionPhaseMillis = millis();

                                LOG_I(TAG_DOOR_STATE, "traction switch FOUND 2 and locking switch 1 OK");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                            // When the traction switch is found when the closing motor is moving in the reverse direction and the locking switch 1 is not in the correct position then start the opening motor in the normal direction
                            else
                            {
                                // Auto reposition sequence switches to moving the opening motor in the normal direction
                                repositionPhase = 0x03; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "traction switch FOUND 2 and locking switch 1 BAD");

                                motorProcess(DOOR_OPENING_ELECTRIC, customSlowMotorSpeed);
                            }
                        }
                    }
                    break;
                case 0x03:
                    {
                        // If after a predifined amount of time the locking switch 1 is not found then start the opening motor in the reverse direction
                        if (millis() > (repositionPhaseMillis + DOOR_REPOSITION_OPENING_DELAY))
                        {
                            // Auto reposition sequence switches to moving the opening motor in the reverse direction
                            repositionPhase = 0x04; repositionPhaseMillis = millis();

                            LOG_W(TAG_DOOR_STATE, "locking switch 1 NOT FOUND 1");

                            motorProcess(DOOR_OPENING_REVERSE_ELECTRIC, customSlowMotorSpeed);
                        }

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00100000) == 0b00000000)
                        {
                            // When the locking switch 1 is found when the opening motor is moving in the normal direction and the traction switch is in the correct position then end the lock reposition sequence
                            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10000000) == 0b00000000)
                            {
                                // End the auto reposition sequence
                                repositionPhase = 0x06; repositionPhaseMillis = millis();

                                LOG_I(TAG_DOOR_STATE, "locking switch 1 FOUND 1 and traction switch OK");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                            // When the locking switch 1 is found when the opening motor is moving in the normal direction and the traction switch is not in the correct position then restart the lock reposition sequence
                            else
                            {
                                // Reset the auto reposition sequence back to the first phase
                                repositionPhase = 0x00; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "locking switch 1 FOUND 1 and traction switch BAD");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                        }
                    }
                    break;
                case 0x04:
                    {
                        // If after a predifined amount of time locking switch 1 is still not found when the opening motor is moving in the reverse direction then restart the lock reposition sequence
                        if (millis() > (repositionPhaseMillis + DOOR_REPOSITION_OPENING_DELAY))
                        {
                            // Reset the auto reposition sequence back to the first phase
                            repositionPhase = 0x00; repositionPhaseMillis = millis();

                            LOG_W(TAG_DOOR_STATE, "locking switch 1 NOT FOUND 2");

                            motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                        }

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b00100000) == 0b00000000)
                        {
                            // When the locking switch 1 is found when the opening motor is moving in the reverse direction and the traction switch is in the correct position then end the lock reposition sequence
                            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & 0b10000000) == 0b00000000)
                            {
                                // End the auto reposition sequence
                                repositionPhase = 0x06; repositionPhaseMillis = millis();

                                LOG_I(TAG_DOOR_STATE, "locking switch 1 FOUND 2 and traction switch OK");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                            // When the locking switch 1 is found when the opening motor is moving in the reverse direction and the traction switch is not in the correct position then restart the lock reposition sequence
                            else
                            {
                                // Reset the auto reposition sequence back to the first phase
                                repositionPhase = 0x00; repositionPhaseMillis = millis();

                                LOG_W(TAG_DOOR_STATE, "locking switch 1 FOUND 2 and traction switch BAD");

                                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                            }
                        }
                    }
                    break;
                case 0x05:
                    {
                        // If after a predifined amount of time the open door state is not found then start the opening motor in the reverse direction
                        if (millis() > (repositionPhaseMillis + DOOR_REPOSITION_OPENING_DELAY))
                        {
                            // Auto reposition sequence switches to moving the opening motor in the reverse direction
                            repositionPhase = 0x04; repositionPhaseMillis = millis();

                            LOG_W(TAG_DOOR_STATE, "open door state NOT FOUND");

                            motorProcess(DOOR_OPENING_REVERSE_ELECTRIC, customSlowMotorSpeed);
                        }

                        if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK) == MASK_DOOR_OPEN_ELECTRIC)
                        {
                            repositionPhase = 0x06;

                            LOG_I(TAG_DOOR_STATE, "open door state FOUND");

                            motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
                        }
                    }
                    break;
                case 0x06:
                    {
                        // In case second try had already set a higher motor speed for the customSlowMotorSPeed
                        customSlowMotorSpeed = config.getCustomSlowMotorSpeed();

                        // Stop the door reposition
                        doorReposition = false;

                        // Unblock all electric lock operations
                        faultyLock = false; secondTry = false;

                        // Reset the auto reposition sequence back to the first phase
                        repositionPhase = 0x00;

                        LOG_I(TAG_DOOR_STATE, "lock reposition end");
                    }
                    break;
            }
        }
    }
    else
    {
        // Error detection during door opening and closing requests
        // If any of the motors spends too much time working without a state change happening then an error is triggered
        if (!faultyLock && !doorReposition && ((doorPhase == DOOR_OPENING_ELECTRIC) || (doorPhase == DOOR_CLOSING_ELECTRIC) || (doorPhase == DOOR_CLOSING_REVERSE_ELECTRIC)))
        {
            if (millis() > (doorPhaseMillis + DOOR_MOVEMENT_ERROR_DELAY))
            {
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // Start the door reposition
                doorReposition = true;

                // Place the door into an unknown state
                doorPhase = DOOR_UNKNOWN_STATE_ELECTRIC;

                // Unblock all electric lock operations
                faultyLock = false; secondTry = false;

                // Reset the timer that will check the elapsed time during the door reposition
                setDoorFaultMillis(millis());

                LOG_E(TAG_DOOR_STATE, "door movement error detected");
            }
        }

        // Door was already closed but the closing motor was still actuated for a short amount of time in the normal direction
        if ((doorState == MASK_DOOR_CLOSED_ELECTRIC) && ((doorPhase == DOOR_ALREADY_CLOSED_ELECTRIC) || (doorPhase == DOOR_UNKNOWN_STATE_ELECTRIC)))
        {
            if (millis() > (doorPhaseMillis + DOOR_CLOSING_DELAY))
            {
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // After the door is closed a small interval is started before the closing motor is engaged in the reverse direction
                doorPhase = DOOR_CLOSING_REVERSE_INTERVAL;

                // Reset the variable that makes sure the small interval has passed
                setDoorPhaseMillis(millis());

                // Reset the door state counter to avoid immediately starting the door reposition again if a future door blocking ocurrs
                doorStateCounter = 0;
            }
        }

        if (doorPhase == DOOR_CLOSING_REVERSE_INTERVAL)
        {
            if (millis() > (doorPhaseMillis + DOOR_CLOSING_INTERVAL_DELAY))
            {
                motorProcess(DOOR_CLOSING_REVERSE_ELECTRIC, customSlowMotorSpeed);

                // The closing motor will now move in the reverse direction until it detects the door as being closed
                doorPhase = DOOR_CLOSING_REVERSE_ELECTRIC;

                // Reset the door state counter to avoid immediately starting the door reposition again if a future door blocking ocurrs
                doorStateCounter = 0;
            }
        }

        if (doorPhase == DOOR_CLOSING_REVERSE_ELECTRIC)
        {
            // When the closing motor is moving in the reverse direction it will only stop when it activates the traction switch
            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK) == MASK_DOOR_CLOSED_ELECTRIC)
            {
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // The closing motor just finished moving in the reverse direction until it detected the door as being closed
                doorPhase = DOOR_CLOSED_ELECTRIC;

                // Unblock all electric lock operations
                faultyLock = false; secondTry = false;

                // Reset the door state counter to avoid immediately starting the door reposition again if a future door blocking ocurrs
                doorStateCounter = 0;
            }
        }

        if (!faultyLock && !doorReposition && !communication.isFactoryMode() && (doorState == MASK_DOOR_INTERMEDIATE_ELECTRIC) && (doorPhase != DOOR_OPENING_ELECTRIC) && (doorPhase != DOOR_CLOSING_ELECTRIC) && (motorState == MOTORS_OFF))
        {
            // This situation happens when the door is detected as being in the intermediate state and the door is not in the process of being opened or closed and because of this it should be considered an error
            if (millis() > (doorPhaseMillis + DOOR_MOVEMENT_ERROR_DELAY))
            {
                motorProcess(DOOR_CLOSING_ELECTRIC, customFastMotorSpeed);

                // The closing motor was started which means the door is in a closing phase
                doorPhase = DOOR_CLOSING_ELECTRIC;

                // Reset the timer that will check the elapsed time during door closing
                setDoorPhaseMillis(millis());

                // A new valid state was detected which resets the counter responsible to detect unrecoginizable states on the electric lock
                doorStateCounter = 0;
            }
        }

        // After the first door reposition ends with insuccess retry it again with the motor at an higher speed
        if (faultyLock && !secondTry && (millis() > (secondTryMillis + DOOR_SECOND_TRY_TIMEOUT)))
        {
            motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

            // Temporarily increase the motor speed used in the door reposition routine
            customSlowMotorSpeed = DEFAULT_FAST_MOTOR_SPEED;

            // Start the door reposition
            doorReposition = true;

            // Place the door into an unknown state
            doorPhase = DOOR_UNKNOWN_STATE_ELECTRIC;

            // Unblock some electric lock operations
            faultyLock = false; secondTry = true;

            // Reset the timer that will check the elapsed time during the door reposition
            setDoorFaultMillis(millis());

            LOG_I(TAG_DOOR_STATE, "lock state is still unrecognizable | starting the second try at electric lock reposition");
        }

        // Handle soft reset closing rotation phase
        if (doorPhase == DOOR_SOFT_RESET_CLOSING_ROTATION)
        {
          //if (millis() > (doorPhaseMillis + DOOR_SOFT_RESET_ROTATION_DELAY))
            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK) == MASK_DOOR_CLOSED_ELECTRIC)
            {
                // Stop the closing motor
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // Start the closing motor in reverse direction at fast speed
                motorProcess(DOOR_OPENING_ELECTRIC, customFastMotorSpeed);

                // Set the door phase to soft reset closing reverse rotation
                doorPhase = DOOR_SOFT_RESET_OPENING_ROTATION;

                // Reset the timer for closing motor reverse rotation
                setDoorPhaseMillis(millis());

                LOG_I(TAG_DOOR_STATE, "soft reset closing rotation completed | starting opening motor");
            }
        }

        // Handle soft reset closing reverse rotation phase
        if (doorPhase == DOOR_SOFT_RESET_CLOSING_REVERSE_ROTATION)
        {
            if (millis() > (doorPhaseMillis + DOOR_SOFT_RESET_CLOSING_REVERSE_ROTATION_DELAY))
            {
                // Stop the closing reverse motor
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // Start the opening motor at fast speed
                motorProcess(DOOR_CLOSING_ELECTRIC, customFastMotorSpeed);

                // Set the door phase to soft reset closing rotation
                doorPhase = DOOR_SOFT_RESET_CLOSING_ROTATION;

                // Reset the timer for opening motor rotation
                setDoorPhaseMillis(millis());

                LOG_I(TAG_DOOR_STATE, "soft reset closing reverse rotation completed | starting closing motor");
            }
        }

        // Handle soft reset opening rotation phase
        if (doorPhase == DOOR_SOFT_RESET_OPENING_ROTATION)
        {
          //if (millis() > (doorPhaseMillis + DOOR_SOFT_RESET_ROTATION_DELAY))
            if ((inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] & DOOR_STATE_MASK) == MASK_DOOR_OPEN_ELECTRIC)
            {
                // Stop the opening motor
                motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                // Set the door state and phase to unknown to allow normal state machine to take over
                doorState = MASK_DOOR_UNKNOWN_ELECTRIC; doorPhase = DOOR_UNKNOWN_STATE_ELECTRIC;

                LOG_I(TAG_DOOR_STATE, "soft reset opening rotation completed | door now open waiting for manual close");
            }
        }
    }
}

void DoorLock::processManualLock()
{
    // The type of lock is defined in the first bit of the oven model
    if ((bitRead( inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] , DOOR_END_STOP_BIT ) != doorState) && (bitRead( inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] , DOOR_END_STOP_BIT ) == DOOR_CLOSED_MANUAL))
    {
        doorState = DOOR_CLOSED_MANUAL;

        LOG_I(TAG_DOOR_STATE, "door was closed");
    }
    if ((bitRead( inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] , DOOR_END_STOP_BIT ) != doorState) && (bitRead( inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07] , DOOR_END_STOP_BIT ) == DOOR_OPEN_MANUAL))
    {
        doorState = DOOR_OPEN_MANUAL;

        LOG_I(TAG_DOOR_STATE, "door was opened");
    }
}

void DoorLock::motorProcess(uint8_t direction, uint8_t speed)
{
    motorState = direction;

    motorSpeed = speed;

    // Set the direction of the motor
    switch (direction)
    {
        case MOTORS_OFF:
            {
                // Set the board states
                bitWrite(communication.getOtherBoardStatesRef(), OPENING_MOTOR_NORMAL_STATE_BIT,  LOW);
                bitWrite(communication.getOtherBoardStatesRef(), OPENING_MOTOR_REVERSE_STATE_BIT, LOW);
                bitWrite(communication.getOtherBoardStatesRef(), CLOSING_MOTOR_NORMAL_STATE_BIT,  LOW);
                bitWrite(communication.getOtherBoardStatesRef(), CLOSING_MOTOR_REVERSE_STATE_BIT, LOW);

                analogWrite(ABRIR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(ABRIR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                analogWrite(FECHAR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(FECHAR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                LOG_D(TAG_MOTORS, "opening and closing motors off");
            }
            break;
        case DOOR_OPENING_ELECTRIC:
            {
                // Set the board states
                bitWrite(communication.getOtherBoardStatesRef(), OPENING_MOTOR_NORMAL_STATE_BIT, HIGH);

                analogWrite(ABRIR_CONTROLLER_IN1_PIN, speed);
                analogWrite(ABRIR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                analogWrite(FECHAR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(FECHAR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                LOG_D(TAG_MOTORS, "opening motor working | forward direction");
            }
            break;
        case DOOR_OPENING_REVERSE_ELECTRIC:
            {
                // Set the board states
                bitWrite(communication.getOtherBoardStatesRef(), OPENING_MOTOR_REVERSE_STATE_BIT, HIGH);

                analogWrite(ABRIR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(ABRIR_CONTROLLER_IN2_PIN, speed);

                analogWrite(FECHAR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(FECHAR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                LOG_D(TAG_MOTORS, "opening motor working | reverse direction");
            }
            break;
        case DOOR_CLOSING_ELECTRIC:
            {
                // Set the board states
                bitWrite(communication.getOtherBoardStatesRef(), CLOSING_MOTOR_NORMAL_STATE_BIT, HIGH);

                analogWrite(ABRIR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(ABRIR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                analogWrite(FECHAR_CONTROLLER_IN1_PIN, speed);
                analogWrite(FECHAR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                LOG_D(TAG_MOTORS, "closing motor working | forward direction");
            }
            break;
        case DOOR_CLOSING_REVERSE_ELECTRIC:
            {
                // Set the board states
                bitWrite(communication.getOtherBoardStatesRef(), CLOSING_MOTOR_REVERSE_STATE_BIT, HIGH);

                analogWrite(ABRIR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(ABRIR_CONTROLLER_IN2_PIN, OUTPUT_OFF);

                analogWrite(FECHAR_CONTROLLER_IN1_PIN, OUTPUT_OFF);
                analogWrite(FECHAR_CONTROLLER_IN2_PIN, speed);

                LOG_D(TAG_MOTORS, "closing motor working | reverse direction");
            }
            break;
    }
}
