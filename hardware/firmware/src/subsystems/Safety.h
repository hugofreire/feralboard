#ifndef SAFETY_H
#define SAFETY_H

#include <Arduino.h>
#include "../config/Definitions.h"

class Safety {
private:
    bool communicationWarningDetected;
    bool enableWarningDetection;
    bool communicationWarningLavagemDetected;
    bool enableWarningLavagemDetection;
    uint32_t communicationWarningMillis;
    uint32_t communicationWarningLavagemMillis;
    uint32_t warningBuzzerMillis;

    uint32_t ventilationErrorMillis;

    bool resistorMonitoringActive;
    bool wasAbove50;
    float resistorStartTemperature;
    uint32_t resistorOnStartTime;
    uint32_t lastResistorCheckTime;

    bool tempErrorDetected;

    bool forceVentilation;
    uint32_t forceVentilationMillis;

    uint8_t boardInternalErrors;

public:
    Safety();

    void init();
    void process();

    void resetExtraSerialTimer();
    void resetRS485SerialTimer();
    void checkCommunicationTimeouts();

    void processWarnings();

    void checkVentilationError();
    void checkResistorError();
    bool shouldForceVentilation();
    void setForceVentilation(bool enable);
    void setTempErrorDetected(bool detected);

    void updateFaultFlags();

    bool isCommunicationWarningDetected() const;
    bool isCommunicationLavagemWarningDetected() const;
    bool isTempErrorDetected() const;
    bool isForceVentilationActive() const;
    uint32_t getForceVentilationMillis() const;

    uint32_t getWarningBuzzerMillis() const;
    void setWarningBuzzerMillis(uint32_t millis);

    void resetCommunicationWarning();
    void resetLavagemWarning();

    uint8_t getBoardInternalErrors() const;
    uint8_t& setBoardInternalErrors();
};

extern Safety safety;

#endif