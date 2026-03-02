/**
 * @file InputManager.h
 * @brief Digital input reading and processing with multiplexer support
 *
 * Responsibilities:
 * - Digital input scanning through 16-channel multiplexer
 * - Input state change detection and logging
 * - Input debouncing for error detection (bits 1, 2, 3)
 * - Door sensor input processing
 * - Input validation and filtering
 */

#ifndef INPUT_MANAGER_H
#define INPUT_MANAGER_H

#include <Arduino.h>
#include "../config/Definitions.h"

class InputManager
{
public:
    // Initialization
    void init();

    // Main processing functions
    void scanInputs();
    void processInputs();

    // State getters
    uint8_t getRealInputs();
    inputsStateUnion& getInputsState();
    uint8_t getInputState(uint8_t byteIndex);

private:

    // Input scanning state machine
    bool readingInputs;
    bool readingDoorInputs;
    uint8_t inputPointer;
    uint32_t inputsReadMillis;
    uint32_t doorInputsReadMillis;
    uint32_t inputReadMillis;

    // Input state storage
    inputsStateUnion inputsState;

    // Debouncing for error inputs (bits 1, 2, 3)
    uint8_t realInputs;
    bool previousState[3];
    uint8_t debounceCounter[3];
    uint32_t inputsDebounceMillis[3];

    // Debug timing
    uint32_t debugInputStateMillis;

    // Internal helper functions
    void readInputChannel();
    void readDoorInputChannel();
    void updateMultiplexerChannel();
    void enableMultiplexer();
    void disableMultiplexer();
};

// Global instance
extern InputManager inputManager;

#endif // INPUT_MANAGER_H