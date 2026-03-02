/**
 * @file Communication.h
 * @brief Serial communication management (80% of communication logic)
 *
 * Responsibilities:
 * - Handle debug, extra, and RS485 serial protocols
 * - Message parsing and CRC validation
 * - Buffer management for incoming/outgoing data
 * - Communication timeout and warning detection
 * - Protocol state machine management
 */

#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>
#include "../config/Definitions.h"

class Communication {
public:
    // Initialization
    void init();

    // Main processing
    void process();

    // State management
    void updateStates();

    // Serial event processing
    void serialProcess();
    void processReceivedBuffer(uint8_t origin);

    // Transmission functions
    void transmitExtraStructure();
    void transmitRS485Structure();

    // Buffer access
    uint8_t* getExtraRequestsBuffer() { return extraRequestsBuffer; }
    uint8_t* getExtraResponseBuffer() { return extraResponseBuffer; }
    uint8_t* getRS485RequestsBuffer() { return RS485RequestsBuffer; }
    uint8_t* getRS485ResponseBuffer() { return RS485ResponseBuffer; }

    // State getters
    bool isLavagemMessageExpected() const { return lavagemMessageExpected; }
    uint32_t getLavagemErrorMillis() const { return lavagemErrorMillis; }

    // State setters
    void setLavagemMessageExpected(bool expected) { lavagemMessageExpected = expected; }
    void setLavagemErrorMillis(uint32_t millis) { lavagemErrorMillis = millis; }

    // Factory mode
    bool isFactoryMode() const { return factoryMode; }
    void setFactoryMode(bool mode) { factoryMode = mode; }

    // Other board states
    byte getOtherBoardStates() const { return otherBoardStates; }
    byte& getOtherBoardStatesRef() { return otherBoardStates; }
    void setOtherBoardStates(byte states) { otherBoardStates = states; }

private:
    // Communication buffers
    uint8_t extraRequestsBuffer[REQUESTS_BUFFER_SIZE];
    uint8_t extraResponseBuffer[RESPONSE_BUFFER_SIZE];
    uint8_t RS485RequestsBuffer[REQUESTS_BUFFER_SIZE];
    uint8_t RS485ResponseBuffer[RESPONSE_BUFFER_SIZE];

    // Buffer management for comparison
    uint8_t lastExtraRequestsBuffer[REQUESTS_BUFFER_SIZE];
    uint8_t lastExtraResponseBuffer[REQUESTS_BUFFER_SIZE];
    uint8_t lastRS485RequestsBuffer[REQUESTS_BUFFER_SIZE];
    uint8_t lastRS485ResponseBuffer[RESPONSE_BUFFER_SIZE];

    // Reception state tracking
    bool extraReceivingData = false;
    bool RS485ReceivingData = false;
    uint8_t extraRequestsBufferIndex = 0;
    uint8_t RS485ResponseBufferIndex = 0;
    uint32_t extraLastByteMillis = 0;
    uint32_t RS485LastByteMillis = 0;
    bool extraMsgReady = false;
    bool rs485MsgReady = false;

    // Lavagem communication state
    bool lavagemMessageExpected = false;
    uint32_t lavagemErrorMillis = 0;
    uint8_t lavagemMissedMessagesCount = 0;

    // Factory mode state
    bool factoryMode = false;

    // Board states for transmission
    byte otherBoardStates = 0;

    // Helper functions
    bool validateChecksum(uint8_t* buffer, uint8_t length, uint8_t checksumLocation);
    void processExtraCommand(uint8_t command, uint8_t data);
    void processLavagemCommand(uint8_t command, uint8_t data);
    void handleDoorCommands(uint8_t command);
    void handleMotorControlCommand(uint8_t motorCommand);
    void handleOvenModelCommand(uint8_t newModel);
    void handleBuzzerCommand(uint8_t buzzerCommand, uint8_t buzzerData);
    void handleMotorSpeedCommand(uint8_t speedType, uint8_t speedValue);
    void handleThermocoupleCommand(uint8_t thermocoupleCount);

    // Build response buffers
    void buildExtraResponseBuffer();
    void buildRS485RequestsBuffer();
};

// Global instance
extern Communication communication;

#endif // COMMUNICATION_H