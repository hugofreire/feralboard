/**
 * @file InputManager.cpp
 * @brief Implementation of digital input reading and processing
 */

#include "InputManager.h"
#include "../utils/Logger.h"
#include "../utils/Utils.h"
#include "../subsystems/Safety.h"

// External references
extern Safety safety;

// Global instance
InputManager inputManager;

void InputManager::init()
{
    // Configure multiplexer control pins
    pinMode(INPUTS_MUX_ENABLE_PIN, OUTPUT);
    pinMode(INPUTS_MUX_SIGNAL_PIN, INPUT);
    pinMode(INPUTS_MUX_CHANNEL_SELECT_0_PIN, OUTPUT);
    pinMode(INPUTS_MUX_CHANNEL_SELECT_1_PIN, OUTPUT);
    pinMode(INPUTS_MUX_CHANNEL_SELECT_2_PIN, OUTPUT);
    pinMode(INPUTS_MUX_CHANNEL_SELECT_3_PIN, OUTPUT);

    // Initialize multiplexer in disabled state
    digitalWrite(INPUTS_MUX_ENABLE_PIN, MULTIPLEXER_DISABLED);

    // Initialize timers
    inputsReadMillis = millis();
    doorInputsReadMillis = millis();
    inputReadMillis = millis();
    debugInputStateMillis = millis();

    // Initialize state
    inputsState.intValue = 0;
    realInputs = 0;
    inputPointer = 0;
    readingInputs = false;
    readingDoorInputs = false;

    LOG_I(TAG_INPUT_MANAGER, "input manager initialized");
}

void InputManager::scanInputs()
{
    // Start reading regular inputs (channels 0-3)
    if (!readingDoorInputs && (millis() > (inputsReadMillis + DELAY_BETWEEN_READING_INPUTS)) && (millis() > (inputReadMillis + DELAY_BETWEEN_READING_INPUT)))
    {
        readingInputs = true; inputsReadMillis = millis(); inputReadMillis = millis(); inputPointer = 0;

        // Enable the multiplexer
        enableMultiplexer();

        // Set channel to 0
        updateMultiplexerChannel();
    }

    // Start reading door inputs (channels 4-7)
    if (!readingInputs && (millis() > (doorInputsReadMillis + DELAY_BETWEEN_READING_DOOR_INPUTS)) && (millis() > (inputReadMillis + DELAY_BETWEEN_READING_INPUT)))
    {
        readingDoorInputs = true; doorInputsReadMillis = millis(); inputReadMillis = millis(); inputPointer = 4;

        // Enable the multiplexer
        enableMultiplexer();

        // Set channel to 4
        updateMultiplexerChannel();
    }

    // Process regular input reading
    if (readingInputs && (millis() > (inputReadMillis + DELAY_BETWEEN_READING_INPUT)))
    {
        readInputChannel();
    }

    // Process door input reading
    if (readingDoorInputs && (millis() > (inputReadMillis + DELAY_BETWEEN_READING_INPUT)))
    {
        readDoorInputChannel();
    }
}

void InputManager::readInputChannel()
{
    // Read the signal pin from the multiplexer
    bool pinState = digitalRead(INPUTS_MUX_SIGNAL_PIN);

    if (bitRead(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], inputPointer) != pinState)
    {
        LOG_D_NO_LN(TAG_INPUT_MANAGER, "channel %02d state has changed to %d", inputPointer, pinState);

        // Insert the pin state value in the inputState structure
        bitWrite(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], inputPointer, pinState);

        char binary_00_07[9], binary_08_15[9];
        formatByteBinary(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], false, binary_00_07);
        formatByteBinary(inputsState.byteArray[OVEN_INPUTS_STATE_08_15], false, binary_08_15);
        LOG_D_CONTINUE(TAG_INPUT_MANAGER, " | inputs channel 00-07 - 0b%s | inputs channel 08-15 - 0b%s", binary_00_07, binary_08_15);
    }

    inputPointer++;

    if (inputPointer == 4)
    {
        readingInputs = false;

        // Disable the multiplexer
        disableMultiplexer();
    }
    else
    {
        // Iterate through all the available channels and get the signal value on the respective channel
        updateMultiplexerChannel();
    }

    // Use a delay between reading each input
    inputReadMillis = millis();
}

void InputManager::readDoorInputChannel()
{
    // Read the signal pin from the multiplexer
    bool pinState = digitalRead(INPUTS_MUX_SIGNAL_PIN);

    if (bitRead(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], inputPointer) != pinState)
    {
        LOG_D_NO_LN(TAG_INPUT_MANAGER_DOOR, "channel %02d state has changed to %d", inputPointer, pinState);

        // Insert the pin state value in the inputState structure
        bitWrite(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], inputPointer, pinState);

        char binary_00_07[9], binary_08_15[9];
        formatByteBinary(inputsState.byteArray[OVEN_INPUTS_STATE_00_07], false, binary_00_07);
        formatByteBinary(inputsState.byteArray[OVEN_INPUTS_STATE_08_15], false, binary_08_15);
        LOG_D_CONTINUE(TAG_INPUT_MANAGER_DOOR, " | inputs channel 00-07 - 0b%s | inputs channel 08-15 - 0b%s", binary_00_07, binary_08_15);
    }

    inputPointer++;

    if (inputPointer == 8)
    {
        readingDoorInputs = false;

        // Disable the multiplexer
        disableMultiplexer();
    }
    else
    {
        // Iterate through all the available channels and get the signal value on the respective channel
        updateMultiplexerChannel();
    }

    // Use a delay between reading each input
    inputReadMillis = millis();
}

void InputManager::processInputs()
{
    // Simplified: report raw input state directly, no debouncing
    for (uint8_t i = 0; i < 3; i++)
    {
        // Bits 1, 2, 3
        uint8_t bitIndex = i + 1;

        bool currentBitState = (inputsState.byteArray[OVEN_INPUTS_STATE_00_07] >> bitIndex) & 0x01;

        if (currentBitState)
        {
            realInputs |= (1 << bitIndex);
        }
        else
        {
            realInputs &= ~(1 << bitIndex);
        }
    }
}

uint8_t InputManager::getRealInputs()
{
    return realInputs;
}

inputsStateUnion& InputManager::getInputsState()
{
    return inputsState;
}

uint8_t InputManager::getInputState(uint8_t byteIndex)
{
    if (byteIndex < 2)
    {
        return inputsState.byteArray[byteIndex];
    }

    return 0;
}

void InputManager::updateMultiplexerChannel()
{
    digitalWrite(INPUTS_MUX_CHANNEL_SELECT_0_PIN, bitRead(inputPointer, 0));
    digitalWrite(INPUTS_MUX_CHANNEL_SELECT_1_PIN, bitRead(inputPointer, 1));
    digitalWrite(INPUTS_MUX_CHANNEL_SELECT_2_PIN, bitRead(inputPointer, 2));
    digitalWrite(INPUTS_MUX_CHANNEL_SELECT_3_PIN, bitRead(inputPointer, 3));
}

void InputManager::enableMultiplexer()
{
    digitalWrite(INPUTS_MUX_ENABLE_PIN, MULTIPLEXER_ENABLED);
}

void InputManager::disableMultiplexer()
{
    digitalWrite(INPUTS_MUX_ENABLE_PIN, MULTIPLEXER_DISABLED);
}