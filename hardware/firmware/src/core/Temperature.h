#ifndef TEMPERATURE_H
#define TEMPERATURE_H

#include <Arduino.h>
#include "../config/Definitions.h"

// Forward declaration to avoid circular dependency
class OutputManager;

/**
 * @brief Temperature management system
 *
 * Handles MAX31856 thermocouple interface, temperature reading,
 * fault detection, and automatic reinitialization.
 */
class Temperature
{
public:
    Temperature();

    // Initialization
    void init();

    // Main processing
    void process();

    // Temperature getters
    float getMainTemperature() const;
    float getPCBTemperature() const;
    float getThermocoupleTemperature(uint8_t channel) const;

    // State getters
    bool isMeasurementActive() const;
    bool isReinitializationMode() const;
    uint8_t getActiveChannel() const;

    // Fault handling
    void updateFaultFlags();

    // Cooling fan control
    void updateCoolingFanOverride(bool& overrideFanState);

    // Configuration getters
    uint8_t getNumberActiveThermocouples() const;

private:
    bool conversionTimeoutFault;
    uint32_t conversionStartMillis;

    // Measurement state
    bool thermocoupleMeasurementActive;
    uint8_t activeThermocouple;
    uint8_t numberActiveThermocouples;

    // Timing
    uint32_t readTemperatureMillis;
    uint32_t debugReadTemperatureMillis;

    // Simulation mode state (only used when SIMULATE_TEMPERATURE_FOR_DEBUG is defined)
    uint32_t randomSeed;

    // Fault detection and recovery
    bool temperatureFaultSet;
    bool temperatureStuckDetected;
    uint32_t temperatureStuckMillis;
    float lastTemperatureValues;
    bool reinitializationMode;
    uint8_t reinitializationCounter;
    uint8_t lastFaultCode;

    // Private helper methods
    #ifdef SIMULATE_TEMPERATURE_FOR_DEBUG
        void processSimulatedTemperature();
    #else
        void processRealTemperature();
        void checkTemperatureStuck();
        void handleReinitialization();
        void handleNormalOperation();
        void processTemperatureReading();
        bool performReinitialization();
    #endif
};

// Global instance
extern Temperature temperature;

#endif
