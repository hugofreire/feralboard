#include "Temperature.h"
#include "../utils/Logger.h"
#include "../subsystems/Safety.h"
#include "../core/OutputManager.h"

// External variable declarations
extern outputStateUnion outputState;
extern OutputManager outputManager;

// Global instance
Temperature temperature;

// Temperature data arrays (moved from main)
temperatureValueTCUnion thermocoupleMeasurements[NUMBER_THERMOCOUPLES_ON_BOARD];
temperatureValueTCUnion temperatureValuePCB;

// Thermocouple converter object (moved from main)
Adafruit_MAX31856 thermocoupleConverter(SELECT_THERMOCOUPLE_PIN);

// SPI settings for MAX31856
const SPISettings MAX31856_SPI_SETTINGS(1000000, MSBFIRST, SPI_MODE1);

// Reinitialization constants
#define FAULTS_BEFORE_REINIT 5
#define MAX_REINIT_ATTEMPTS 20

Temperature::Temperature() :
    conversionTimeoutFault(false),
    conversionStartMillis(0),
    thermocoupleMeasurementActive(false),
    activeThermocouple(MAIN_THERMOCOUPLE_SELECTED),
    numberActiveThermocouples(DEFAULT_THERMOCOUPLE_AMOUNT),
    readTemperatureMillis(0),
    debugReadTemperatureMillis(0),
    randomSeed(0),
    temperatureFaultSet(false),
    temperatureStuckDetected(false),
    temperatureStuckMillis(0),
    lastTemperatureValues(999.0f),
    reinitializationMode(false),
    reinitializationCounter(0),
    lastFaultCode(0)
{
}

void Temperature::init()
{
    // Configure thermocouple pins
    pinMode(THERMOCOUPLE_MUX_CHANNEL_SELECT_1_PIN, OUTPUT);
    digitalWrite(THERMOCOUPLE_MUX_CHANNEL_SELECT_1_PIN, bitRead(MAIN_THERMOCOUPLE_SELECTED, 0));
    pinMode(THERMOCOUPLE_MUX_CHANNEL_SELECT_0_PIN, OUTPUT);
    digitalWrite(THERMOCOUPLE_MUX_CHANNEL_SELECT_0_PIN, bitRead(MAIN_THERMOCOUPLE_SELECTED, 1));

    pinMode(DATA_READY_THERMOCOUPLE_PIN, INPUT);
    pinMode(FAULT_THERMOCOUPLE_PIN, INPUT);
    pinMode(SELECT_THERMOCOUPLE_PIN, OUTPUT);
    digitalWrite(SELECT_THERMOCOUPLE_PIN, SPI_CHIP_DESELECTED);

    pinMode(THERMOCOUPLE_MUX_ENABLE_PIN, OUTPUT);
    digitalWrite(THERMOCOUPLE_MUX_ENABLE_PIN, MULTIPLEXER_ENABLED);

    readTemperatureMillis = millis();
    debugReadTemperatureMillis = millis();
    randomSeed = 0;

    thermocoupleMeasurementActive = false;
    temperatureFaultSet = false;
    temperatureStuckDetected = false;
    temperatureStuckMillis = 0;
    lastTemperatureValues = 999.0f;
    reinitializationMode = false;
    reinitializationCounter = 0;
    lastFaultCode = 0;

    #ifdef SIMULATE_TEMPERATURE_FOR_DEBUG

        delay(STARTING_DELAY);

        thermocoupleMeasurements[activeThermocouple].floatValue = 0.0f;
        temperatureValuePCB.floatValue = 0.0f;

    #else

        // Starting delay for the thermocouple converter
        delay(STARTING_DELAY);

        // MAX31856 works correctly when SPI MODE 1 due to the change in the polarity signals
        SPI.beginTransaction(MAX31856_SPI_SETTINGS);

        // Start the oven thermocouple converter
        if (thermocoupleConverter.begin())
        {
            // Select the type of thermocouple that is being used (library default is thermocouple type K)
          //thermocoupleConverter.setThermocoupleType(MAX31856_TCTYPE_K);

            // Set a low and high temperature threshold for the cold junction
          //thermocoupleConverter.setColdJunctionFaultThreshholds(COLD_JUNCTION_LOW_TEMPERATURE, COLD_JUNCTION_HIGH_TEMPERATURE);

            // Set a low and high temperature threshold for the thermocouple
          //thermocoupleConverter.setTempFaultThreshholds(THERMOCOUPLE_LOW_TEMPERATURE, THERMOCOUPLE_HIGH_TEMPERATURE);

            // Set the noise filter to the thermocouple converter (library default filter is 60Hz)
          //thermocoupleConverter.setNoiseFilter(MAX31856_NOISE_FILTER_60HZ);

            // Set the conversion mode for the thermocouple converter (library default is one shot conversion which has a hard delay)
            thermocoupleConverter.setConversionMode(MAX31856_ONESHOT_NOWAIT);

            // Start the first conversion
            thermocoupleConverter.triggerOneShot();

            LOG_I(TAG_TEMPERATURE, "thermocouple was detected");
        }
        else
        {
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT, HIGH);

            LOG_E(TAG_TEMPERATURE, "no thermocouple was detected");
        }

        // End the SPI transaction
        SPI.endTransaction();

    #endif
}

void Temperature::process()
{
    #ifdef SIMULATE_TEMPERATURE_FOR_DEBUG

        processSimulatedTemperature();

    #else

        processRealTemperature();

    #endif

    // Update cooling fan override state based on PCB temperature
    bool overrideFanState = outputManager.getOverrideFanState();

    updateCoolingFanOverride(overrideFanState);

    outputManager.setOverrideFanState(overrideFanState);
}

float Temperature::getMainTemperature() const
{
    return thermocoupleMeasurements[MAIN_THERMOCOUPLE_SELECTED].floatValue;
}

float Temperature::getPCBTemperature() const
{
    return temperatureValuePCB.floatValue;
}

float Temperature::getThermocoupleTemperature(uint8_t channel) const
{
    if (channel < NUMBER_THERMOCOUPLES_ON_BOARD)
    {
        return thermocoupleMeasurements[channel].floatValue;
    }

    return 0.0f;
}

bool Temperature::isMeasurementActive() const
{
    return thermocoupleMeasurementActive;
}

bool Temperature::isReinitializationMode() const
{
    return reinitializationMode;
}

uint8_t Temperature::getActiveChannel() const
{
    return activeThermocouple;
}

void Temperature::updateFaultFlags()
{
    // Fault flags are updated directly in the processing methods
}

void Temperature::updateCoolingFanOverride(bool& overrideFanState)
{
    if (temperatureValuePCB.floatValue >= COOLING_FAN_OVERRIDE_TEMPERATURE)
    {
        digitalWrite(COOLING_FAN_CONTROL_PIN, COOLING_FAN_ON);

        // PCB temperature is high so the fan is on regardless of what is received from the extra serial
        overrideFanState = true;
    }
    else
    {
        overrideFanState = false;
    }
}

#ifdef SIMULATE_TEMPERATURE_FOR_DEBUG

void Temperature::processSimulatedTemperature()
{
    if (millis() > (debugReadTemperatureMillis + DELAY_BETWEEN_SIMULATED_TEMPERATURE_READINGS))
    {
        // Seed the random generator once
        if (randomSeed == 0)
        {
            randomSeed = millis(); ::randomSeed(randomSeed);
        }

        // Force a PCB temperature reading
        temperatureValuePCB.floatValue = 30.0f;

        // Generate random decimal part (0.00 to 0.99)
        float randomDecimal = (float)(random(0, 100)) / 100.0f;

        // Force a thermocouple temperature reading
        if (bitRead(outputState.byteArray[OVEN_OUTPUTS_STATE_00_07], RESISTOR_BIT))
        {
            // When the output controlling the oven resistor is activated the temperature is increased by one degree
            thermocoupleMeasurements[activeThermocouple].floatValue += (SIMULATED_TEMPERATURE_CHANGE + randomDecimal);
        }
        else
        {
            // When the output controlling the oven resistor is deactivated the temperature is decreased by one degree
            thermocoupleMeasurements[activeThermocouple].floatValue -= (SIMULATED_TEMPERATURE_CHANGE - randomDecimal);

            // The temperature cannot be lower than the minimum predifined temperature for simulation
            if (thermocoupleMeasurements[activeThermocouple].floatValue < MIN_SIMULATED_TEMPERATURE)
            {
                thermocoupleMeasurements[activeThermocouple].floatValue = MIN_SIMULATED_TEMPERATURE + randomDecimal;
            }
        }

        LOG_I(TAG_TEMPERATURE, "thermocouple converter internal temperature: %d.%02d°C | integer value: %d",
        
        (int)temperatureValuePCB.floatValue, (int)((temperatureValuePCB.floatValue - (int)temperatureValuePCB.floatValue) * 100), (uint8_t)temperatureValuePCB.floatValue);

        LOG_I(TAG_TEMPERATURE, "channel %d thermocouple temperature: %d.%02d°C",

        activeThermocouple, (int)thermocoupleMeasurements[activeThermocouple].floatValue, (int)((thermocoupleMeasurements[activeThermocouple].floatValue - (int)thermocoupleMeasurements[activeThermocouple].floatValue) * 100));

        // The simulated temperature is increased or decreased at a predifined interval
        debugReadTemperatureMillis = millis();
    }
}

#else

void Temperature::processRealTemperature()
{
    // Check for stuck temperature
    checkTemperatureStuck();

    if (temperatureFaultSet && (millis() > (readTemperatureMillis + DELAY_BETWEEN_THERMOCOUPLE_READINGS)))
    {
        thermocoupleMeasurementActive = false;
    }

    // Main temperature reading and reinitialization loop
    if (!thermocoupleMeasurementActive && (millis() > (readTemperatureMillis + DELAY_BETWEEN_THERMOCOUPLE_READINGS)))
    {
        // MAX31856 works correctly when SPI MODE 1 due to the change in the polarity signals
        SPI.beginTransaction(MAX31856_SPI_SETTINGS);

        // Check if we are in reinitialization mode
        if (reinitializationMode)
        {
            handleReinitialization();
        }
        else
        {
            handleNormalOperation();
        }

        // Add a small delay between readings
        readTemperatureMillis = millis();

        // End the SPI transaction
        SPI.endTransaction();
    }

    // A thermocouple reading was started
    if (thermocoupleMeasurementActive)
    {
        processTemperatureReading();
    }
}

void Temperature::checkTemperatureStuck()
{
    // Only check for stuck temperature readings if we have a valid reading (not 0.0f which already indicates an error)
    if ((thermocoupleMeasurements[activeThermocouple].floatValue != 0.0f)
    &&  (thermocoupleMeasurements[activeThermocouple].floatValue < UNREALISTIC_HIGH_TEMPERATURE)
    &&  (thermocoupleMeasurements[activeThermocouple].floatValue > UNREALISTIC_LOW_TEMPERATURE))
    {
        // Compare with 0.01ºC precision (two decimal places)
        float lastTemp = roundf(lastTemperatureValues * 100.0f) / 100.0f;

        float currentTemp = roundf(thermocoupleMeasurements[activeThermocouple].floatValue * 100.0f) / 100.0f;

        if ((currentTemp == lastTemp) && (lastTemperatureValues != 999.0f))
        {
            // Temperature has not changed
            if (temperatureStuckMillis == 0)
            {
                // Start counting
                temperatureStuckMillis = millis();
            }
            // 30 seconds
            else if ((millis() - temperatureStuckMillis) > 30000)
            {
                if (!temperatureFaultSet)
                {
                    temperatureFaultSet = true; safety.setTempErrorDetected(true);

                    // Trigger reinitialization mode for stuck temperature
                    if (!reinitializationMode)
                    {
                        reinitializationMode = true; reinitializationCounter = 0;

                        LOG_W(TAG_TEMPERATURE, "main thermocouple entering reinitialization mode after stuck temperature detection");
                    }

                    // In case the thermocouple measurement was active then stop it
                    thermocoupleMeasurementActive = false;

                    // Use the red LED to signal an error
                    digitalWrite(LED_RED_SIGNAL_PIN, LED_ENABLED);

                    if (!safety.isForceVentilationActive())
                    {
                      //safety.setForceVentilation(true);
                    }

                    LOG_W(TAG_TEMPERATURE, "main thermocouple stuck detection | temperature unchanged for 30 seconds at %d.%02d degrees",
                    
                    (int)currentTemp, (int)((currentTemp - (int)currentTemp) * 100));
                }
            }
            // 10 seconds
            else if ((millis() - temperatureStuckMillis) > 10000)
            {
                if (!temperatureStuckDetected)
                {
                    LOG_W(TAG_TEMPERATURE, "main thermocouple stuck detection | temperature unchanged for 10 seconds at %d.%02d degrees | possible conversion failure",
                    
                    (int)currentTemp, (int)((currentTemp - (int)currentTemp) * 100));

                    temperatureStuckDetected = true;
                }
            }
        }
        else
        {
            // Temperature changed so reset counters
            temperatureStuckDetected = false;

            lastTemperatureValues = thermocoupleMeasurements[activeThermocouple].floatValue;

            temperatureStuckMillis = 0;
        }
    }
}

bool Temperature::performReinitialization()
{
    // Reinitialize the oven thermocouple converter
    if (thermocoupleConverter.begin())
    {
        // Select the type of thermocouple that is being used (library default is thermocouple type K)
      //thermocoupleConverter.setThermocoupleType(MAX31856_TCTYPE_K);

        // Set a low and high temperature threshold for the cold junction
      //thermocoupleConverter.setColdJunctionFaultThreshholds(COLD_JUNCTION_LOW_TEMPERATURE, COLD_JUNCTION_HIGH_TEMPERATURE);

        // Set a low and high temperature threshold for the thermocouple
      //thermocoupleConverter.setTempFaultThreshholds(THERMOCOUPLE_LOW_TEMPERATURE, THERMOCOUPLE_HIGH_TEMPERATURE);

        // Set the noise filter to the thermocouple converter (library default filter is 60Hz)
      //thermocoupleConverter.setNoiseFilter(MAX31856_NOISE_FILTER_60HZ);

        // Set the conversion mode for the thermocouple converter (library default is one shot conversion which has a hard delay)
        thermocoupleConverter.setConversionMode(MAX31856_ONESHOT_NOWAIT);

        // Start the first conversion
      //thermocoupleConverter.triggerOneShot();

        LOG_W(TAG_TEMPERATURE, "main thermocouple reinitialization attempt %d", reinitializationCounter);

        return true;
    }
    else
    {
        bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT, HIGH);

        LOG_E(TAG_TEMPERATURE, "main thermocouple reinitialization attempt %d failed | no thermocouple detected", reinitializationCounter);

        return false;
    }
}

void Temperature::handleReinitialization()
{
    // Increment reinitialization counter
    reinitializationCounter++;

    if (lastFaultCode & MAX31856_FAULT_OVUV)
    {
        thermocoupleConverter.clearFaultRegister();
    }

    // Attempt reinitialization
    bool reinitSuccess = performReinitialization();

    // Check if we've exceeded max attempts - set error bits but continue trying
    if (reinitializationCounter >= MAX_REINIT_ATTEMPTS)
    {
        // Use the red LED to signal an error
        digitalWrite(LED_RED_SIGNAL_PIN, LED_ENABLED);

        if (!safety.isForceVentilationActive())
        {
            safety.setForceVentilation(true);

            LOG_E(TAG_TEMPERATURE, "main thermocouple maximum reinitialization attempts reached (%d) | forcing ventilation", MAX_REINIT_ATTEMPTS);
        }

        // Set the appropriate error bits based on what triggered reinitialization
        if (temperatureFaultSet)
        {
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT, HIGH);
        }
        else if (conversionTimeoutFault)
        {
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT, HIGH);
        }
        else
        {
            if (lastFaultCode & MAX31856_FAULT_OVUV)
            {
                bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OVUV_BIT, HIGH);
            }
            if (lastFaultCode & MAX31856_FAULT_OPEN)
            {
                bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OPEN_BIT, HIGH);
            }
        }
    }

    // Always read and display faults during reinitialization
    uint8_t fault = thermocoupleConverter.readFault();

    // Identify and display the faults
    if (fault)
    {
        // Store the fault code for later use
        lastFaultCode = fault;

        if (fault & MAX31856_FAULT_OVUV)
        {
            LOG_E(TAG_TEMPERATURE, "faults detected in the main thermocouple | fault: thermocouple over/under voltage");
        }
        if (fault & MAX31856_FAULT_OPEN)
        {
            LOG_E(TAG_TEMPERATURE, "faults detected in the main thermocouple | fault: thermocouple is open - no connections");
        }
    }
    else
    {
        // Faults successefuly cleared
        if ((lastFaultCode != NO_VALUE) && reinitSuccess)
        {
            LOG_W(TAG_TEMPERATURE, "all faults successfully cleared on attempt %d", reinitializationCounter);
        }
    }

    // Always try to start a new conversion if reinitialization succeeded
    if (reinitSuccess)
    {
        thermocoupleMeasurementActive = true;

        // Start a new conversion regardless of fault status
        thermocoupleConverter.triggerOneShot();
    }
    else
    {
        // Reinitialization failed - remain in reinitialization mode
        thermocoupleMeasurementActive = false;
    }
}

void Temperature::handleNormalOperation()
{
    // Normal operation mode - not in reinitialization

    // Check if there is a fault with the main thermocouple
    uint8_t fault = thermocoupleConverter.readFault();

    // Identify the faults
    if (fault)
    {
        // Store the fault code for later use
        lastFaultCode = fault;

        // Trigger a thermocouple reinitialization if a fault is detected
        if (!reinitializationMode)
        {
            reinitializationMode = true; reinitializationCounter = 0;
        }

        LOG_W(TAG_TEMPERATURE, "main thermocouple entering reinitialization mode after fault detection");

        if (fault & MAX31856_FAULT_OVUV)
        {
            LOG_E(TAG_TEMPERATURE, "faults detected in the main thermocouple | fault: thermocouple over/under voltage");
        }
        if (fault & MAX31856_FAULT_OPEN)
        {
            LOG_E(TAG_TEMPERATURE, "faults detected in the main thermocouple | fault: thermocouple is open - no connections");
        }

        // Fault detected so do not start measurement
        thermocoupleMeasurementActive = false;
    }
    else
    {
        thermocoupleMeasurementActive = true;

        // No fault - start a new conversion
        thermocoupleConverter.triggerOneShot();
    }
}

void Temperature::processTemperatureReading()
{
    bool conversionReady = false;

    if (conversionStartMillis == RESET_VALUE)
    {
        conversionStartMillis = millis();
    }
    /*
        PRIMARY CHECK USING HARDWARE
    */
    if (!digitalRead(DATA_READY_THERMOCOUPLE_PIN))
    {
        conversionReady = true;
    }
    /*
        IF TIMEOUT IS APPROACHING ALSO CHECK VIA SOFTWARE
    */
    else if ((millis() - conversionStartMillis) > 200)
    {
        SPI.beginTransaction(MAX31856_SPI_SETTINGS);

        if (thermocoupleConverter.conversionComplete())
        {
            conversionReady = true;

            LOG_W(TAG_TEMPERATURE, "DRDY pin not responding but conversion complete via SPI | possible DRDY hardware fault\n");
        }
        SPI.endTransaction();
    }
    if (((millis() - conversionStartMillis) > 500)  && !conversionReady)
    {
        /*
            CONVERSION TOOK TOO LONG SO THERE IS A POSSIBLE HARDWARE ISSUE ON DRDY PIN
        */
        thermocoupleMeasurementActive = false; conversionStartMillis = RESET_VALUE;
        /*
            TRIGGER A THERMOCOUPLE REINITIALIZATION IF A FAULT IS DETECTED
        */
        if (!reinitializationMode)
        {
            reinitializationMode = true; reinitializationCounter = RESET_VALUE;

            conversionTimeoutFault = true;

            LOG_W(TAG_TEMPERATURE, "DRDY timeout | conversion never completed\n");
        }
    }
    // Check via software or hardware if the conversion is complete
    if (conversionReady)
    {
        // MAX31856 works correctly when SPI MODE 1 due to the change in the polarity signals
        SPI.beginTransaction(MAX31856_SPI_SETTINGS);

        // The internal temperature of the thermocouple converter is used as PCB temperature
        temperatureValuePCB.floatValue = thermocoupleConverter.readCJTemperature();

        // Read the temperature value of the thermocouple in degrees Celsius when the conversion is complete
        thermocoupleMeasurements[activeThermocouple].floatValue = thermocoupleConverter.readThermocoupleTemperature();

        // End the SPI transaction
        SPI.endTransaction();

        // Check if this is a valid reading
        bool validReading = true;

        // Check for unrealistic readings that indicate open circuit

        // Typical open circuit readings are above 1000°C or below -100°C
        if ((thermocoupleMeasurements[activeThermocouple].floatValue < UNREALISTIC_LOW_TEMPERATURE)
        ||  (thermocoupleMeasurements[activeThermocouple].floatValue > UNREALISTIC_HIGH_TEMPERATURE))
        {
            validReading = false;

            // This is likely an open circuit condition
            // Trigger reinitialization mode but don't set high temperature fault
            if (!reinitializationMode)
            {
                reinitializationMode = true; reinitializationCounter = 0;

                // Set the last fault code to open circuit
                lastFaultCode = MAX31856_FAULT_OPEN;

                LOG_W(TAG_TEMPERATURE, "main thermocouple unrealistic reading detected (%d.%02d°C) | likely open circuit - entering reinitialization mode",

                (int)thermocoupleMeasurements[activeThermocouple].floatValue, (int)((thermocoupleMeasurements[activeThermocouple].floatValue - (int)thermocoupleMeasurements[activeThermocouple].floatValue) * 100));
            }
        }
        else if ((thermocoupleMeasurements[activeThermocouple].floatValue < THERMOCOUPLE_LOW_TEMPERATURE)
        ||       (thermocoupleMeasurements[activeThermocouple].floatValue > THERMOCOUPLE_HIGH_TEMPERATURE))
        {
            validReading = false;

            LOG_W(TAG_TEMPERATURE, "temperature range trigger | thermocouple converter internal temperature: %d.%02d°C | integer value: %d",
                  
            (int)temperatureValuePCB.floatValue, (int)((temperatureValuePCB.floatValue - (int)temperatureValuePCB.floatValue) * 100), (uint8_t)temperatureValuePCB.floatValue);

            LOG_W(TAG_TEMPERATURE, "temperature range trigger | channel %d thermocouple temperature: %d.%02d°C", 
    
            activeThermocouple, (int)thermocoupleMeasurements[activeThermocouple].floatValue, (int)((thermocoupleMeasurements[activeThermocouple].floatValue - (int)thermocoupleMeasurements[activeThermocouple].floatValue) * 100));

            // Use the red LED to signal an error
            digitalWrite(LED_RED_SIGNAL_PIN, LED_ENABLED);

            // Set the thermocouple fault associated with high temperature trigger
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT, HIGH);

            if (!safety.isForceVentilationActive())
            {
                safety.setForceVentilation(true);

                LOG_W(TAG_TEMPERATURE, "main thermocouple maximum temperature reached | forcing ventilation");
            }
        }

        // Only exit reinitialization mode on a successful and valid reading
        if (validReading)
        {
            // Reset all error tracking for this channel
            reinitializationCounter = 0;

            // Exit reinitialization mode if we were in it
            if (reinitializationMode)
            {
                reinitializationMode = false;

                temperatureFaultSet = false;

                temperatureStuckDetected = false;

                temperatureStuckMillis = 0;

                lastFaultCode = 0;

                LOG_I(TAG_TEMPERATURE, "main thermocouple exiting reinitialization mode | successful reading obtained");
            }

            // Clear the thermocouple faults not associated with high temperature triggers
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OVUV_BIT, LOW);
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT, LOW);

            if (!safety.isForceVentilationActive() && bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT))
            {
                bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT, LOW);
            }

            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OPEN_BIT, LOW);
            bitWrite(safety.setBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT, LOW);

            LOG_I(TAG_TEMPERATURE, "thermocouple converter internal temperature: %d.%02d°C | integer value: %d",
      
            (int)temperatureValuePCB.floatValue, (int)((temperatureValuePCB.floatValue - (int)temperatureValuePCB.floatValue) * 100), (uint8_t)temperatureValuePCB.floatValue);

            LOG_I(TAG_TEMPERATURE, "channel %d thermocouple temperature: %d.%02d°C",

            activeThermocouple, (int)thermocoupleMeasurements[activeThermocouple].floatValue, (int)((thermocoupleMeasurements[activeThermocouple].floatValue - (int)thermocoupleMeasurements[activeThermocouple].floatValue) * 100));

            // Clear the error on the red LED but only if there are no temperature errors
            if (!bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_BIT)
            &&  !bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_OPEN_BIT)
            &&  !bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT)
            &&  !bitRead(safety.getBoardInternalErrors(), FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT))
            {
                digitalWrite(LED_RED_SIGNAL_PIN, LED_DISABLED);
            }
        }

        // Thermocouple reading is complete
        thermocoupleMeasurementActive = false;
    }
}

#endif

uint8_t Temperature::getNumberActiveThermocouples() const
{
    return numberActiveThermocouples;
}
