
#include "src/config/Definitions.h"
#include "src/config/Config.h"
#include "src/utils/Logger.h"
#include "src/utils/Utils.h"
#include "src/subsystems/Buzzer.h"
#include "src/subsystems/Safety.h"
#include "src/subsystems/DoorLock.h"
#include "src/core/Communication.h"
#include "src/core/InputManager.h"
#include "src/core/OutputManager.h"
#include "src/core/Temperature.h"

void setup()
{
    debugSerial.begin(SERIAL_DEBUG_BAUD_RATE);

    debugSerial.setTimeout(SERIAL_DEBUG_COMMUNICATION_TIMEOUT);

    // Connector to the extra serial port is connected to the alternative pins
    extraSerial.swap(ALTERNATIVE_PINS_EXTRA_SERIAL);

    // After configuration of the alternative serial 1 pins we can start it
    extraSerial.begin(SERIAL_EXTRA_BAUD_RATE);              extraSerial.setTimeout(SERIAL_EXTRA_COMMUNICATION_TIMEOUT);

    // Serial 3
    rs485Serial.begin(SERIAL_RS485_BAUD_RATE);              rs485Serial.setTimeout(SERIAL_RS485_COMMUNICATION_TIMEOUT);

    // Start the SPI
    // SPI is used to read the thermocouples and set the outputs of the shift registers
    SPI.begin();

    // Start the wire
    // Wire is used to set the voltage that controls the motor speed
    Wire.begin();

    // Initialize enhanced logging
    logger.init();
    logger.setLogOutputMode(LOG_OUTPUT_BINARY);

    // Initialize configuration from EEPROM
    config.init();
    buzzer.init();
    safety.init();
    communication.init();
    inputManager.init();
    outputManager.init();
    temperature.init();
    doorLock.init();

    // Small delay so the startup buzzer can be heard
    delay(500);
}

void loop()
{
    // Toggle the strobe input of the microprocessor monitor every 25ms
    outputManager.processStrobe();

    // Get the state of all the inputs
    inputManager.scanInputs();

    // Process the inputs
    inputManager.processInputs();

    // Refresh the output state according to received messages
    outputManager.setOutputs(outputManager.getOutputControlMode());

    // Refresh the resistor power according to received messages
  //outputManager.setResistorPower();

    // Get the door state
    doorLock.process();

    // Process buzzer requests
    buzzer.process();

    // Always listening for data in the serial ports
    communication.process();

    // Read the temmperature of a thermocouple
    temperature.process();

    // Update communication states for transmission
    communication.updateStates();

    // Process program warnings
    safety.process();
}

// doorProcess() moved to DoorLock::process()

// motorProcess() moved to DoorLock::motorProcess()

// getInputs() moved to InputManager::scanInputs()

// processInputs() moved to InputManager::processInputs()

// setOutputs() moved to OutputManager::setOutputs()

// setMotorSpeedLevel() moved to OutputManager::setMotorSpeedLevel()

// setResistorPower() moved to OutputManager::setResistorPower()

// strobeProcess() moved to OutputManager::processStrobe()


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
