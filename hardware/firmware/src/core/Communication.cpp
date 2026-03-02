/**
 * @file Communication.cpp
 * @brief Serial communication management implementation
 */

#include "Communication.h"
#include "../config/Config.h"
#include "../subsystems/Safety.h"
#include "../subsystems/Buzzer.h"
#include "../subsystems/DoorLock.h"
#include "../utils/Logger.h"
#include "../utils/Utils.h"
#include "InputManager.h"
#include "OutputManager.h"
#include <EEPROM.h>

// External dependencies from main file
extern Safety safety;
extern Buzzer buzzer;
extern Config config;
extern InputManager inputManager;
extern OutputManager outputManager;
extern DoorLock doorLock;
extern uint8_t resistorPowerValue;
extern outputStateUnion outputState;
extern temperatureValueTCUnion thermocoupleMeasurements[];
extern uint8_t inputsInversionMask0;
extern uint8_t inputsInversionMask1;
extern uint8_t inputsStrobe;
extern temperatureValueTCUnion temperatureValuePCB;

// Global instance
Communication communication;

void Communication::init()
{
    // Configure RS485 driver enable pin
    pinMode(RS485_DRIVER_ENABLE_PIN, OUTPUT);
    digitalWrite(RS485_DRIVER_ENABLE_PIN, RS485_DRIVER_RECEIVING);

    // Initialize buffers
    memset(extraRequestsBuffer,     0, sizeof(extraRequestsBuffer));
    memset(extraResponseBuffer,     0, sizeof(extraResponseBuffer));
    memset(lastExtraRequestsBuffer, 0, sizeof(lastExtraRequestsBuffer));
    memset(lastExtraResponseBuffer, 0, sizeof(lastExtraResponseBuffer));
    memset(RS485RequestsBuffer,     0, sizeof(RS485RequestsBuffer));
    memset(RS485ResponseBuffer,     0, sizeof(RS485ResponseBuffer));
    memset(lastRS485RequestsBuffer, 0, sizeof(lastRS485RequestsBuffer));
    memset(lastRS485ResponseBuffer, 0, sizeof(lastRS485ResponseBuffer));

    // Initialize reception state
    extraReceivingData = false;
    RS485ReceivingData = false;
    extraRequestsBufferIndex = 0;
    RS485ResponseBufferIndex = 0;
    extraLastByteMillis = 0;
    RS485LastByteMillis = 0;
    extraMsgReady = false;
    rs485MsgReady = false;

    // Initialize lavagem state
    lavagemErrorMillis = 0;
    lavagemMessageExpected = false;
    lavagemMissedMessagesCount = 0;

    // Initialize factory mode (simplified: always on by default)
    factoryMode = true;
}

void Communication::process()
{
    // Process serial data
    serialProcess();

    // Process at most one complete message per loop pass
    if (extraMsgReady)
    {
        processReceivedBuffer(ORIGIN_SERIAL_EXTRA); extraMsgReady = false;

        // Each time a full message is received, reset the communication timeout
        safety.resetExtraSerialTimer();
    }
    else if (rs485MsgReady)
    {
        processReceivedBuffer(ORIGIN_SERIAL_RS485); rs485MsgReady = false;

        // Each time a full message is received, reset the communication timeout
        safety.resetRS485SerialTimer();
    }

    // Check for lavagem message timeout
    if (lavagemMessageExpected && (millis() > (lavagemErrorMillis + LAVAGEM_MESSAGE_ERROR_TIMEOUT)))
    {
        // Increment missed message counter
        lavagemMissedMessagesCount++;

        LOG_W(TAG_COMMUNICATION, "lavagem message expected but not received | missed count - %d/80", lavagemMissedMessagesCount);

        // Check if threshold reached (80 missed messages = 20 seconds at 250ms intervals)
        if (lavagemMissedMessagesCount >= 80)
        {
            // Trigger communication error
            bitWrite(RS485ResponseBuffer[LAVAGEM_INTERNAL_ERRORS_LOCATION], FAULT_LAVAGEM_COMMUNICATION_BIT, HIGH);

            LOG_E(TAG_COMMUNICATION, "lavagem communication error triggered after 20 seconds of no response");

            // Reset counter to avoid repeated triggers
            lavagemMissedMessagesCount = 0;
        }

        transmitExtraStructure(); lavagemMessageExpected = false;
    }
}

void Communication::serialProcess()
{
    // Process extra serial port
    while (extraSerial.available())
    {
        // Start receiving or continue receiving data
        if (!extraReceivingData)
        {
            extraReceivingData = true; extraRequestsBufferIndex = 0;
        }

        // Keep receiving while the message is not complete
        if (extraRequestsBufferIndex < REQUESTS_BUFFER_SIZE)
        {
            extraRequestsBuffer[extraRequestsBufferIndex++] = extraSerial.read(); extraLastByteMillis = millis();
        }
        else
        {
            // Defensive - discard overflow
            extraSerial.read(); extraLastByteMillis = millis();
        }

        // Check if we have received a full message
        if (extraRequestsBufferIndex >= REQUESTS_BUFFER_SIZE)
        {
            // Full message received - calculate checksum of received data (excluding the checksum byte itself)
            uint8_t calculatedChecksum = calculateChecksum(extraRequestsBuffer, REQUESTS_BUFFER_SIZE - 1);

            if (calculatedChecksum == extraRequestsBuffer[REQUESTS_CHECKSUM_LOCATION])
            {
                // Extra request buffer is full and should be processed later
                extraMsgReady = true;
            }
            else
            {
                LOG_W(TAG_SERIAL_EXTRA, "serial extra checksum mismatch | expected - %02X | got - %02X", calculatedChecksum, extraRequestsBuffer[RESPONSE_CHECKSUM_LOCATION]);

                for (uint8_t i = 0; i < extraRequestsBufferIndex; i++)
                {
                    LOG_D(TAG_SERIAL_EXTRA_ECHO_HEX_RX, "serial extra byte %d - %02X", i, extraRequestsBuffer[i]);
                }
            }

            // Reset for next message
            extraReceivingData = false; extraRequestsBufferIndex = 0;
        }
    }

    // Process rs485 serial port
    while (rs485Serial.available())
    {
        // Start receiving or continue receiving data
        if (!RS485ReceivingData)
        {
            RS485ReceivingData = true; RS485ResponseBufferIndex = 0;
        }

        // Keep receiving while the message is not complete
        if (RS485ResponseBufferIndex < RESPONSE_BUFFER_SIZE)
        {
            RS485ResponseBuffer[RS485ResponseBufferIndex++] = rs485Serial.read(); RS485LastByteMillis = millis();
        }
        else
        {
            // Defensive - discard overflow
            rs485Serial.read(); RS485LastByteMillis = millis();
        }

        // Check if we have received a full message
        if (RS485ResponseBufferIndex >= RESPONSE_BUFFER_SIZE)
        {
            // Full message received - calculate checksum of received data (excluding the checksum byte itself)
            uint8_t calculatedChecksum = calculateChecksum(RS485ResponseBuffer, RESPONSE_BUFFER_SIZE - 1);

            if (calculatedChecksum == RS485ResponseBuffer[RESPONSE_CHECKSUM_LOCATION])
            {
                // Set the bit indicating communication ok with the lavagem board
                bitWrite(RS485ResponseBuffer[LAVAGEM_INTERNAL_ERRORS_LOCATION], FAULT_LAVAGEM_COMMUNICATION_BIT, LOW );

                // Extra request buffer is full and should be processed later
                rs485MsgReady = true;
            }
            else
            {
                LOG_W(TAG_SERIAL_RS485, "serial rs485 checksum mismatch | expected - %02X | got - %02X", calculatedChecksum, extraRequestsBuffer[RESPONSE_CHECKSUM_LOCATION]);

                for (uint8_t i = 0; i < RS485ResponseBufferIndex; i++)
                {
                    LOG_D(TAG_SERIAL_RS485_ECHO_HEX_RX, "serial rs485 byte %d - %02X", i, RS485ResponseBuffer[i]);
                }
            }

            // Reset for next message
            RS485ReceivingData = false; RS485ResponseBufferIndex = 0;
        }
    }

    // Timeout handling for extra serial
    if (extraReceivingData && ((millis() - extraLastByteMillis) > SERIAL_TIMEOUT_MS))
    {
        // Timeout occurred - partial message received
        LOG_W(TAG_WARNING, "serial extra timeout has occurred | bytes received - %d", extraRequestsBufferIndex);

        for (uint8_t i = 0; i < extraRequestsBufferIndex; i++)
        {
            LOG_D(TAG_SERIAL_EXTRA_ECHO_HEX_RX, "serial extra byte %d - %02X", i, extraRequestsBuffer[i]);
        }

        // Flush any remaining bytes in the serial buffer
        while (extraSerial.available()) { extraSerial.read(); }

        // Reset for the next message
        extraReceivingData = false; extraRequestsBufferIndex = 0;
    }

    // Timeout handling for RS485 serial
    if (RS485ReceivingData && ((millis() - RS485LastByteMillis) > SERIAL_TIMEOUT_MS))
    {
        // Timeout occurred - partial message received
        LOG_W(TAG_WARNING, "serial rs485 timeout has occurred | bytes received - %d", RS485ResponseBufferIndex);

        for (uint8_t i = 0; i < RS485ResponseBufferIndex; i++)
        {
            LOG_D(TAG_SERIAL_RS485_ECHO_HEX_RX, "serial rs485 byte %d - %02X", i, RS485ResponseBuffer[i]);
        }

        // Flush any remaining bytes in the serial buffer
        while (rs485Serial.available()) { rs485Serial.read(); }

        // Reset for the next message
        RS485ReceivingData = false; RS485ResponseBufferIndex = 0;
    }
}

void Communication::processReceivedBuffer(uint8_t origin)
{
    switch (origin)
    {
        case ORIGIN_SERIAL_EXTRA:
            {
                // Update approved output states
                outputManager.setAprovedOutputState(OVEN_OUTPUTS_STATE_00_07, extraRequestsBuffer[OVEN_OUTPUTS_STATE_00_07]);
                outputManager.setAprovedOutputState(OVEN_OUTPUTS_STATE_08_15, extraRequestsBuffer[OVEN_OUTPUTS_STATE_08_15]);
                outputManager.setAprovedOutputState(OVEN_OUTPUTS_STATE_16_23, extraRequestsBuffer[OVEN_OUTPUTS_STATE_16_23]);
                outputManager.setAprovedOutputState(OVEN_OUTPUTS_STATE_EXTRA, extraRequestsBuffer[OVEN_OUTPUTS_STATE_EXTRA]);

                // Check if buffer changed for logging
                bool bufferChanged = false;

                for (uint8_t i = 0; i < REQUESTS_BUFFER_SIZE; i++)
                {
                    if (lastExtraRequestsBuffer[i] != extraRequestsBuffer[i])
                    {
                        bufferChanged = true; break;
                    }
                }
                if (bufferChanged)
                {
                    LOG_D_NO_LN(TAG_SERIAL_EXTRA_ECHO_RX, "serial extra message received - ");

                    for (uint8_t i = 0; i < REQUESTS_BUFFER_SIZE; i++)
                    {
                        LOG_D_CONTINUE_NO_LN(TAG_SERIAL_EXTRA_ECHO_RX, "%02X ", extraRequestsBuffer[i]);
                    }

                    LOG_D_CONTINUE(TAG_SERIAL_EXTRA_ECHO_RX, "");

                    // Update last buffer
                    memcpy(lastExtraRequestsBuffer, extraRequestsBuffer, REQUESTS_BUFFER_SIZE);
                }

                // If oven has lavagem, transmit to rs485 and expect response
                if (bitRead(config.getOvenModel(), OVEN_MODEL_WASHING_BIT)) { transmitRS485Structure(); lavagemMessageExpected = true; setLavagemErrorMillis(millis()); }

                // Process the command
                processExtraCommand(extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION], extraRequestsBuffer[COMMAND_OVEN_DT_LOCATION]);

                // Echo back if no lavagem active
                if (!bitRead(config.getOvenModel(), OVEN_MODEL_WASHING_BIT)) { transmitExtraStructure(); }
            }
            break;
        case ORIGIN_SERIAL_RS485:
            {
                // Check if message is for this board
                if (bitRead(RS485ResponseBuffer[RESPONSE_DESTINATION_IDENTIFIER_LOCATION], OVEN_MODEL_POSITION_BIT) != bitRead(config.getOvenModel(), OVEN_MODEL_POSITION_BIT))
                {
                    // Message for another board
                    LOG_D_NO_LN(TAG_SERIAL_RS485_ECHO_RX, "serial rs485 message received was intended to another board - ");

                    for (uint8_t i = 0; i < RESPONSE_BUFFER_SIZE; i++)
                    {
                        LOG_D_CONTINUE_NO_LN(TAG_SERIAL_RS485_ECHO_RX, "%02X ", RS485ResponseBuffer[i]);
                    }

                    LOG_D_CONTINUE(TAG_SERIAL_RS485_ECHO_RX, "| do nothing");
                }
                else
                {
                    // Message is for this board
                    // Reset missed message counter since we received a valid response
                    lavagemMissedMessagesCount = 0;

                    bool bufferChanged = false;

                    for (uint8_t i = 0; i < RESPONSE_BUFFER_SIZE; i++)
                    {
                        if (lastRS485ResponseBuffer[i] != RS485ResponseBuffer[i])
                        {
                            bufferChanged = true; break;
                        }
                    }
                    if (bufferChanged)
                    {
                        LOG_D_NO_LN(TAG_SERIAL_RS485_ECHO_RX, "serial rs485 message received - ");

                        for (uint8_t i = 0; i < RESPONSE_BUFFER_SIZE; i++)
                        {
                            LOG_D_CONTINUE_NO_LN(TAG_SERIAL_RS485_ECHO_RX, "%02X ", RS485ResponseBuffer[i]);
                        }

                        LOG_D_CONTINUE(TAG_SERIAL_RS485_ECHO_RX, "");

                        // Update last buffer
                        memcpy(lastRS485ResponseBuffer, RS485ResponseBuffer, RESPONSE_BUFFER_SIZE);
                    }

                    // Echo back to raspberry pi
                    transmitExtraStructure(); lavagemMessageExpected = false;
                }
            }
            break;
    }
}

void Communication::processExtraCommand(uint8_t command, uint8_t data)
{
    switch (command)
    {
        case SET_STATES_COMMAND:
            {
                // Set the outputs
                outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
            }
            break;
        case GET_STATES_COMMAND:
            {
                // Do nothing here
            }
            break;
        case RST_STATES_COMMAND:
            {
                // Reset outputs to initial state
                extraRequestsBuffer[OVEN_OUTPUTS_STATE_00_07] = 0;
                extraRequestsBuffer[OVEN_OUTPUTS_STATE_08_15] = 0;
                extraRequestsBuffer[OVEN_OUTPUTS_STATE_16_23] = 0;
                extraRequestsBuffer[OVEN_OUTPUTS_STATE_EXTRA] = 0;

                // Reset resistor power
                outputManager.setResistorPowerValue(0);

                // Set the outputs
                outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
            }
            break;
        case FACTORY_MODE_COMMAND:
            {
                // Simplified: factory mode is always on, command is a no-op
                LOG_I(TAG_FACTORY_MODE, "factory mode command received | factory mode is always on");

                // Set the outputs
                outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
            }
            break;
        case OPEN_DOOR_COMMAND:
            {
                handleDoorCommands(command);
            }
            break;
        case CLOSE_DOOR_COMMAND:
            {
                handleDoorCommands(command);
            }
            break;
        case MOTOR_CONTROL_COMMAND:
            {
                handleMotorControlCommand(data);
            }
            break;
        case OVEN_MODEL_COMMAND:
            {
                handleOvenModelCommand(data);
            }
            break;
        case BUZZER_STRENGTH_COMMAND:
            {
                handleBuzzerCommand(command, data);
            }
            break;
        case BUZZER_FREQUENCY_COMMAND:
            {
                handleBuzzerCommand(command, data);
            }
            break;
        case MOTOR_SLOW_SPEED_COMMAND:
            {
                handleMotorSpeedCommand(command, data);
            }
            break;
        case MOTOR_FAST_SPEED_COMMAND:
            {
                handleMotorSpeedCommand(command, data);
            }
            break;
        case SET_NUMBER_THERMOCOUPLES_COMMAND:
            {
                handleThermocoupleCommand(data);
            }
            break;
        case TURN_OFF_FORCED_VENTILATION:
            {
                LOG_I(TAG_SYSTEM, "turning off forced ventilation");

                safety.setForceVentilation(false);

                // Set the outputs immediately
                outputManager.setOutputs(OUTPUTS_CONTROL_IMMEDIATE);
            }
            break;
        default:
            {
                // Unrecognized command
                extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = UNRECOGNIZED_COMMAND;
            }
            break;
    }
}

void Communication::handleDoorCommands(uint8_t command)
{
    doorLock.setDoorStateCounter(0);

    if (command == OPEN_DOOR_COMMAND)
    {
        // Open door if in valid state
        if (!doorLock.isFaultyLock() && !doorLock.isDoorReposition() && ((doorLock.getDoorState() == MASK_DOOR_INTERMEDIATE_ELECTRIC) || (doorLock.getDoorState() == MASK_DOOR_CLOSED_ELECTRIC)) && (doorLock.getMotorState() == MOTORS_OFF))
        {
            doorLock.motorProcess(DOOR_OPENING_ELECTRIC, config.getCustomFastMotorSpeed());

            doorLock.setDoorPhase(DOOR_OPENING_ELECTRIC);

            doorLock.setDoorPhaseMillis(millis());
        }
    }
    else if (command == CLOSE_DOOR_COMMAND)
    {
        // Close door if in valid state
        if (!doorLock.isFaultyLock() && !doorLock.isDoorReposition() && (doorLock.getDoorState() == MASK_DOOR_INTERMEDIATE_ELECTRIC) && (doorLock.getMotorState() == MOTORS_OFF))
        {
            doorLock.motorProcess(DOOR_CLOSING_ELECTRIC, config.getCustomFastMotorSpeed());

            doorLock.setDoorPhase(DOOR_CLOSING_ELECTRIC);

            doorLock.setDoorPhaseMillis(millis());
        }

        // If door already closed, actuate motor briefly
        else if (!doorLock.isFaultyLock() && !doorLock.isDoorReposition() && (doorLock.getDoorState() == MASK_DOOR_CLOSED_ELECTRIC) && (doorLock.getMotorState() == MOTORS_OFF))
        {
            doorLock.motorProcess(DOOR_CLOSING_ELECTRIC, config.getCustomSlowMotorSpeed());

            doorLock.setDoorPhase(DOOR_ALREADY_CLOSED_ELECTRIC);

            doorLock.setDoorPhaseMillis(millis());
        }
    }

    // Set the outputs
    outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
}

void Communication::handleMotorControlCommand(uint8_t motorCommand)
{
    switch (motorCommand)
    {
        case MOTORS_OFF:
            {
                doorLock.motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);
            }
            break;
        case OPEN_MOTOR_NORMAL_DIRECTION:
            {
                doorLock.motorProcess(DOOR_OPENING_ELECTRIC, config.getCustomFastMotorSpeed());
            }
            break;
        case OPEN_MOTOR_REVERSE_DIRECTION:
            {
                doorLock.motorProcess(DOOR_OPENING_REVERSE_ELECTRIC, config.getCustomFastMotorSpeed());
            }
            break;
        case CLOSE_MOTOR_NORMAL_DIRECTION:
            {
                doorLock.motorProcess(DOOR_CLOSING_ELECTRIC, config.getCustomFastMotorSpeed());
            }
            break;
        case CLOSE_MOTOR_REVERSE_DIRECTION:
            {
                doorLock.motorProcess(DOOR_CLOSING_REVERSE_ELECTRIC, config.getCustomFastMotorSpeed());
            }
            break;
        case START_LOCK_RESET:
            {
                // Start the closing motor in the normal direction for one full rotation at fast speed
                doorLock.motorProcess(DOOR_CLOSING_REVERSE_ELECTRIC, config.getCustomFastMotorSpeed());

                // Set the door phase to soft reset closing rotation
                doorLock.setDoorPhase(DOOR_SOFT_RESET_CLOSING_REVERSE_ROTATION);

                // Unlock all electric lock operations
                doorLock.setFaultyLock(false); doorLock.setSecondTry(false);

                // Reset the timer that will check the elapsed time during the soft reset closing rotation
                doorLock.setDoorPhaseMillis(millis());
            }
            break;
        case START_LOCK_REPOSITION:
            {
                if (doorLock.isFaultyLock())
                {
                    doorLock.motorProcess(MOTORS_OFF, MOTORS_OFF_SPEED);

                    // Start door reposition
                    doorLock.setDoorReposition(true);

                    doorLock.setDoorPhase(DOOR_UNKNOWN_STATE_ELECTRIC);

                    doorLock.setFaultyLock(false); doorLock.setSecondTry(false);

                    doorLock.setDoorFaultMillis(millis());
                }
                else
                {
                    // Invalid command
                    extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;
                }
            }
            break;
        default:
            {
                // Invalid command
                extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;
            }
            break;
    }
}

void Communication::handleOvenModelCommand(uint8_t newModel)
{
    if (newModel > OVEN_TOP_LAVAGEM_ON_ELECTRIC)
    {
        // Invalid value
        extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

        char binary_oven_model[9];
        formatByteBinary(newModel, false, binary_oven_model);
        LOG_W(TAG_EEPROM, "received invalid new oven model value - %d (0b%s)", newModel, binary_oven_model);
    }
    else
    {
        config.setOvenModel(newModel);

        char binary_oven_model[9];
        formatByteBinary(config.getOvenModel(), false, binary_oven_model);
        LOG_I(TAG_EEPROM, "new oven model value - %d (0b%s)", config.getOvenModel(), binary_oven_model);
    }
    // Set the outputs
    outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
}

void Communication::handleBuzzerCommand(uint8_t command, uint8_t data)
{
    if (command == BUZZER_STRENGTH_COMMAND)
    {
        if (data > BUZZER_DEFAULT_STRENGTH)
        {
            extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

            LOG_W(TAG_EEPROM, "received invalid new buzzer strength value - %d", data);
        }
        else
        {
            config.setBuzzerStrength(data);

            LOG_I(TAG_EEPROM, "new buzzer strength value - %d", data);
        }
    }
    else if (command == BUZZER_FREQUENCY_COMMAND)
    {
        if ((data == BUZZER_FREQUENCY_1)
        ||  (data == BUZZER_FREQUENCY_4)
        ||  (data == BUZZER_FREQUENCY_8)
        ||  (data == BUZZER_FREQUENCY_16))
        {
            config.setBuzzerFrequency(data);

            LOG_I(TAG_EEPROM, "new buzzer frequency value - %d", data);
        }
        else
        {
            extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

            LOG_W(TAG_EEPROM, "received invalid new buzzer frequency value - %d", data);
        }
    }
    // Set the outputs
    outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
}

void Communication::handleMotorSpeedCommand(uint8_t speedType, uint8_t speedValue)
{
    if (speedType == MOTOR_SLOW_SPEED_COMMAND)
    {
        if (speedValue < DEFAULT_SLOW_MOTOR_SPEED)
        {
            extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

            LOG_W(TAG_EEPROM, "received invalid new custom slow motor speed value - %d", speedValue);
        }
        else
        {
            // Update customSLowMotorSpeed in real time
            if (doorLock.getMotorSpeed() == config.getCustomSlowMotorSpeed()) { doorLock.motorProcess(doorLock.getMotorState(), extraRequestsBuffer[COMMAND_OVEN_DT_LOCATION]); }
 
            config.setCustomSlowMotorSpeed(speedValue);

            LOG_I(TAG_EEPROM, "new custom slow motor speed value - %d", speedValue);
        }
    }
    else if (speedType == MOTOR_FAST_SPEED_COMMAND)
    {
        if (speedValue < DEFAULT_SLOW_MOTOR_SPEED)
        {
            extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

            LOG_W(TAG_EEPROM, "received invalid new custom fast motor speed value - %d", speedValue);
        }
        else
        {
            // Update customFastMotorSpeed in real time
            if (doorLock.getMotorSpeed() == config.getCustomFastMotorSpeed()) { doorLock.motorProcess(doorLock.getMotorState(), extraRequestsBuffer[COMMAND_OVEN_DT_LOCATION]); }

            config.setCustomFastMotorSpeed(speedValue);

            LOG_I(TAG_EEPROM, "new custom fast motor speed value - %d", speedValue);
        }
    }
    // Set the outputs
    outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
}

void Communication::handleThermocoupleCommand(uint8_t thermocoupleCount)
{
    if (thermocoupleCount > NUMBER_THERMOCOUPLES_ON_BOARD)
    {
        extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION] = INVALID_COMMAND;

        LOG_W(TAG_EEPROM, "received invalid number of active thermocouples value - %d", thermocoupleCount);
    }
    else
    {
        config.setNumberActiveThermocouples(thermocoupleCount);

        LOG_I(TAG_EEPROM, "new number of active thermocouples value - %d", thermocoupleCount);
    }
    // Set the outputs
    outputManager.setOutputs(OUTPUTS_CONTROL_DELAYED);
}

void Communication::updateStates()
{
    // Indicates if a fault was detected in the ELECTRIC lock
    bitWrite(safety.setBoardInternalErrors(), FAULT_ELECTRIC_LOCK_BIT, doorLock.isFaultyLock());

    // Indicates if the factory mode is enabled in the board
    bitWrite(this->otherBoardStates, FACTORY_MODE_STATE_BIT, factoryMode);

    // Indicates if the door reposition is in progress
    bitWrite(this->otherBoardStates, DOOR_REPOSITION_IN_PROGRESS_BIT, doorLock.isDoorReposition());

    // Indicates forced ventilation is on
    safety.updateFaultFlags();

    // Indicates the state of the electric lock
    if (doorLock.isFaultyLock() || doorLock.isDoorReposition())
    {
        // Clear bit 6 & 7 in order to set to correctly set the door state in the misc board states variable
        this->otherBoardStates &= DEBOUNCED_DOOR_STATE_MASK;

        // Door state unknown
        this->otherBoardStates |= DEBOUNCED_DOOR_STATE_UNKNOWN;
    }
    else if ((doorLock.getDoorState() == MASK_DOOR_OPEN_ELECTRIC) && (doorLock.getDoorPhase() == DOOR_OPEN_ELECTRIC))
    {
        // Clear bit 6 & 7 in order to set to correctly set the door state in the misc board states variable
        this->otherBoardStates &= DEBOUNCED_DOOR_STATE_MASK;

        // Door detected open
        this->otherBoardStates |= DEBOUNCED_DOOR_STATE_OPEN;
    }
    else if ((doorLock.getDoorState() == MASK_DOOR_INTERMEDIATE_ELECTRIC) && (doorLock.getDoorPhase() == DOOR_OPEN_ELECTRIC))
    {
        // Clear bit 6 & 7 in order to set to correctly set the door state in the misc board states variable
        this->otherBoardStates &= DEBOUNCED_DOOR_STATE_MASK;

        // Door detected intermediate
        this->otherBoardStates |= DEBOUNCED_DOOR_STATE_INTERMEDIATE;
    }
    else if ((factoryMode && (doorLock.getDoorState() == MASK_DOOR_CLOSED_ELECTRIC)) || ((doorLock.getDoorState() == MASK_DOOR_CLOSED_ELECTRIC) && (doorLock.getDoorPhase() == DOOR_CLOSED_ELECTRIC)))
    {
        // Clear bit 6 & 7 in order to set to correctly set the door state in the misc board states variable
        this->otherBoardStates &= DEBOUNCED_DOOR_STATE_MASK;

        // Door detected closed
        this->otherBoardStates |= DEBOUNCED_DOOR_STATE_CLOSED;
    }
    else
    {
        // Clear bit 6 & 7 in order to set to correctly set the door state in the misc board states variable
        this->otherBoardStates &= DEBOUNCED_DOOR_STATE_MASK;

        // Door state unknown
        this->otherBoardStates |= DEBOUNCED_DOOR_STATE_UNKNOWN;
    }
}

void Communication::transmitExtraStructure()
{
    buildExtraResponseBuffer();

    // Calculate and add checksum
    extraResponseBuffer[RESPONSE_CHECKSUM_LOCATION] = calculateChecksum(extraResponseBuffer, RESPONSE_BUFFER_SIZE - 1);

    // Transmit the buffer
    extraSerial.write(extraResponseBuffer, RESPONSE_BUFFER_SIZE);

    // Wait for the serial port to finish transmitting all the data
    extraSerial.flush();

    bool bufferChanged = false;

    // Only print the response message if it was changed
    for (uint8_t i = 0; i < RESPONSE_BUFFER_SIZE; i++)
    {
        if (lastExtraResponseBuffer[i] != extraResponseBuffer[i])
        {
            bufferChanged = true; break;
        }
    }
    if (bufferChanged)
    {
        LOG_D_NO_LN(TAG_SERIAL_EXTRA_ECHO_TX, "serial extra message transmitted - ");

        for (uint8_t i = 0; i < RESPONSE_BUFFER_SIZE; i++)
        {
            LOG_D_CONTINUE_NO_LN(TAG_SERIAL_EXTRA_ECHO_TX, "%02X ", extraResponseBuffer[i]);
        }

        LOG_D_CONTINUE(TAG_SERIAL_EXTRA_ECHO_TX, "");

        // Update last buffer
        memcpy(lastExtraResponseBuffer, extraResponseBuffer, RESPONSE_BUFFER_SIZE);
    }
}

void Communication::transmitRS485Structure()
{
    buildRS485RequestsBuffer();

    // Calculate and add checksum
    RS485RequestsBuffer[REQUESTS_CHECKSUM_LOCATION] = calculateChecksum(RS485RequestsBuffer, REQUESTS_BUFFER_SIZE - 1);

    // Place the RS485 driver in transmission mode
    digitalWrite(RS485_DRIVER_ENABLE_PIN, RS485_DRIVER_TRANSMITTING);

    // Transmit the data
    rs485Serial.write(RS485RequestsBuffer, REQUESTS_BUFFER_SIZE);

    // Wait for the serial port to finish transmitting all the data
    rs485Serial.flush();

    // Place the RS485 driver in receiving mode
    digitalWrite(RS485_DRIVER_ENABLE_PIN, RS485_DRIVER_RECEIVING);

    bool bufferChanged = false;

    // Only print the transmit message if it was changed
    for (uint8_t i = 0; i < REQUESTS_BUFFER_SIZE; i++)
    {
        if (lastRS485RequestsBuffer[i] != RS485RequestsBuffer[i])
        {
            bufferChanged = true; break;
        }
    }
    if (bufferChanged)
    {
        LOG_D_NO_LN(TAG_SERIAL_RS485_ECHO_TX, "serial rs485 message transmitted - ");

        for (uint8_t i = 0; i < REQUESTS_BUFFER_SIZE; i++)
        {
            LOG_D_CONTINUE_NO_LN(TAG_SERIAL_RS485_ECHO_TX, "%02X ", RS485RequestsBuffer[i]);
        }

        LOG_D_CONTINUE(TAG_SERIAL_RS485_ECHO_TX, "");

        // Update last buffer
        memcpy(lastRS485RequestsBuffer, RS485RequestsBuffer, REQUESTS_BUFFER_SIZE);
    }
}

void Communication::buildExtraResponseBuffer()
{
    // Bytes 0-2 - output states
    extraResponseBuffer[OVEN_OUTPUTS_STATE_00_07_LOCATION] = outputManager.getOutputState().byteArray[OVEN_OUTPUTS_STATE_00_07];
    extraResponseBuffer[OVEN_OUTPUTS_STATE_08_15_LOCATION] = outputManager.getOutputState().byteArray[OVEN_OUTPUTS_STATE_08_15];
    extraResponseBuffer[OVEN_OUTPUTS_STATE_16_23_LOCATION] = outputManager.getOutputState().byteArray[OVEN_OUTPUTS_STATE_16_23];

    // Byte 3 - extra outputs
    bitWrite(extraResponseBuffer[OVEN_OUTPUTS_STATE_EXTRA_LOCATION], BUZZER_INTERNAL_BIT, buzzer.getInternalState());
    bitWrite(extraResponseBuffer[OVEN_OUTPUTS_STATE_EXTRA_LOCATION], COOLING_FAN_BIT,     outputManager.getCoolingFanState());

    // Bytes 4-5 - input states
    extraResponseBuffer[OVEN_INPUTS_STATE_00_07_LOCATION] = inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_00_07];
    extraResponseBuffer[OVEN_INPUTS_STATE_08_15_LOCATION] = inputManager.getInputsState().byteArray[OVEN_INPUTS_STATE_08_15];

    // Bytes 6-9 - main thermocouple temperature
    extraResponseBuffer[OVEN_TEMPERATURE_BYTE_0_LOCATION] = thermocoupleMeasurements[MAIN_THERMOCOUPLE_SELECTED].byteArray[0];
    extraResponseBuffer[OVEN_TEMPERATURE_BYTE_1_LOCATION] = thermocoupleMeasurements[MAIN_THERMOCOUPLE_SELECTED].byteArray[1];
    extraResponseBuffer[OVEN_TEMPERATURE_BYTE_2_LOCATION] = thermocoupleMeasurements[MAIN_THERMOCOUPLE_SELECTED].byteArray[2];
    extraResponseBuffer[OVEN_TEMPERATURE_BYTE_3_LOCATION] = thermocoupleMeasurements[MAIN_THERMOCOUPLE_SELECTED].byteArray[3];

    // Bytes 10-13 - extra 1 thermocouple temperature
    extraResponseBuffer[EXTRA_1_TEMPERATURE_BYTE_0_LOCATION] = thermocoupleMeasurements[EXTRA_1_THERMOCOUPLE_SELECTED].byteArray[0];
    extraResponseBuffer[EXTRA_1_TEMPERATURE_BYTE_1_LOCATION] = thermocoupleMeasurements[EXTRA_1_THERMOCOUPLE_SELECTED].byteArray[1];
    extraResponseBuffer[EXTRA_1_TEMPERATURE_BYTE_2_LOCATION] = thermocoupleMeasurements[EXTRA_1_THERMOCOUPLE_SELECTED].byteArray[2];
    extraResponseBuffer[EXTRA_1_TEMPERATURE_BYTE_3_LOCATION] = thermocoupleMeasurements[EXTRA_1_THERMOCOUPLE_SELECTED].byteArray[3];

    // Bytes 14-17 - extra 2 thermocouple temperature
    extraResponseBuffer[EXTRA_2_TEMPERATURE_BYTE_0_LOCATION] = thermocoupleMeasurements[EXTRA_2_THERMOCOUPLE_SELECTED].byteArray[0];
    extraResponseBuffer[EXTRA_2_TEMPERATURE_BYTE_1_LOCATION] = thermocoupleMeasurements[EXTRA_2_THERMOCOUPLE_SELECTED].byteArray[1];
    extraResponseBuffer[EXTRA_2_TEMPERATURE_BYTE_2_LOCATION] = thermocoupleMeasurements[EXTRA_2_THERMOCOUPLE_SELECTED].byteArray[2];
    extraResponseBuffer[EXTRA_2_TEMPERATURE_BYTE_3_LOCATION] = thermocoupleMeasurements[EXTRA_2_THERMOCOUPLE_SELECTED].byteArray[3];

    // Bytes 18-21 - extra 3 thermocouple temperature
    extraResponseBuffer[EXTRA_3_TEMPERATURE_BYTE_0_LOCATION] = thermocoupleMeasurements[EXTRA_3_THERMOCOUPLE_SELECTED].byteArray[0];
    extraResponseBuffer[EXTRA_3_TEMPERATURE_BYTE_1_LOCATION] = thermocoupleMeasurements[EXTRA_3_THERMOCOUPLE_SELECTED].byteArray[1];
    extraResponseBuffer[EXTRA_3_TEMPERATURE_BYTE_2_LOCATION] = thermocoupleMeasurements[EXTRA_3_THERMOCOUPLE_SELECTED].byteArray[2];
    extraResponseBuffer[EXTRA_3_TEMPERATURE_BYTE_3_LOCATION] = thermocoupleMeasurements[EXTRA_3_THERMOCOUPLE_SELECTED].byteArray[3];

    // Byte 22 - pcb temperature
    extraResponseBuffer[OVEN_PCB_TEMPERATURE_LOCATION] = (uint8_t)temperatureValuePCB.floatValue;

    // Byte 23 - board internal errors
    extraResponseBuffer[OVEN_INTERNAL_ERRORS_LOCATION] = safety.getBoardInternalErrors();

    // Byte 24 - other states
    extraResponseBuffer[OVEN_OTHER_STATES_LOCATION] = this->otherBoardStates;

    // Byte 25 - oven model
    extraResponseBuffer[OVEN_MODEL_LOCATION] = config.getOvenModel();

    // Byte 26 - internal buzzer volume
    extraResponseBuffer[OVEN_INTERNAL_BUZZER_VOLUME_LOCATION] = config.getBuzzerStrength();

    // Byte 27 - echo last command
    extraResponseBuffer[OVEN_ECHO_LAST_COMMAND_LOCATION] = extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION];

    // Bytes 28-38 - lavagem data from rs485 response
    for (uint8_t i = 0; i < 11; i++)
    {
        extraResponseBuffer[LAVAGEM_OUTPUTS_STATE_00_04_RESPONSE_LOCATION + i] = RS485ResponseBuffer[LAVAGEM_OUTPUTS_STATE_00_04_RESPONSE_LOCATION + i];
    }
}

void Communication::buildRS485RequestsBuffer()
{
    // Bytes 0-3 - output states
    RS485RequestsBuffer[OVEN_OUTPUTS_STATE_00_07_LOCATION] = extraRequestsBuffer[OVEN_OUTPUTS_STATE_00_07_LOCATION];
    RS485RequestsBuffer[OVEN_OUTPUTS_STATE_08_15_LOCATION] = extraRequestsBuffer[OVEN_OUTPUTS_STATE_08_15_LOCATION];
    RS485RequestsBuffer[OVEN_OUTPUTS_STATE_16_23_LOCATION] = extraRequestsBuffer[OVEN_OUTPUTS_STATE_16_23_LOCATION];
    RS485RequestsBuffer[OVEN_OUTPUTS_STATE_EXTRA_LOCATION] = extraRequestsBuffer[OVEN_OUTPUTS_STATE_EXTRA_LOCATION];

    // Bytes 4-5 - command and data
    RS485RequestsBuffer[COMMAND_OVEN_ID_LOCATION] = extraRequestsBuffer[COMMAND_OVEN_ID_LOCATION];
    RS485RequestsBuffer[COMMAND_OVEN_DT_LOCATION] = extraRequestsBuffer[COMMAND_OVEN_DT_LOCATION];

    // Check for oven errors that should trigger lavagem outputs off
    if (bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OVUV_BIT)
    ||  bitRead(safety.getBoardInternalErrors(), FAULT_FORCED_VENTILATION_BIT)
    ||  bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT)
    ||  bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT)
    ||  bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OPEN_BIT)
    ||  bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT)
    ||  bitRead(inputManager.getRealInputs(), ELECTRIC_PROTECTION_BIT)
    ||  bitRead(inputManager.getRealInputs(), OVEN_OVER_TEMPERATURE_BIT)
    ||  bitRead(inputManager.getRealInputs(), MOTOR_OVER_TEMPERATURE_BIT))
    {
        // Turn off lavagem outputs
        RS485RequestsBuffer[LAVAGEM_OUTPUTS_STATE_00_04_REQUESTS_LOCATION] = 0;
    }
    else
    {
        // Copy lavagem output state from extra requests
        RS485RequestsBuffer[LAVAGEM_OUTPUTS_STATE_00_04_REQUESTS_LOCATION] = extraRequestsBuffer[LAVAGEM_OUTPUTS_STATE_00_04_REQUESTS_LOCATION];
    }

    // Byte 7 - lavagem command
    RS485RequestsBuffer[COMMAND_LAVAGEM_ID_LOCATION] = extraRequestsBuffer[COMMAND_LAVAGEM_ID_LOCATION];

    // Byte 8 - lavagem data
    RS485RequestsBuffer[COMMAND_LAVAGEM_DT_LOCATION] = extraRequestsBuffer[COMMAND_LAVAGEM_DT_LOCATION];

    // Byte 9 - message origin identifier
    RS485RequestsBuffer[REQUESTS_ORIGIN_IDENTIFIER_LOCATION] = config.getOvenModel();
}