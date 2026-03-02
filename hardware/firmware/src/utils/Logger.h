#ifndef LOGGER_H
#define LOGGER_H

#include <Arduino.h>
#include <stdarg.h>
#include "Utils.h"

#ifndef FIRMWARE_VERSION
#define FIRMWARE_VERSION "1.2.7"
#endif

// Log levels
enum logLevel {
    LOG_ERROR   = 0,
    LOG_WARNING = 1,
    LOG_INFO    = 2,
    LOG_DEBUG   = 4
};

// Current log level - higher number = more verbose
#define CURRENT_LOG_LEVEL LOG_DEBUG

// Protocol features
#define LOG_PROTOCOL_VERSION    0x01
#define FRAME_START_BYTE        0x7E
#define FRAME_ESCAPE_BYTE       0x7D
#define FRAME_XOR_MASK          0x20

// Names for the log levels
extern const char* logLevelNames[];

// Program tags for different subsystems
enum logTag {
    TAG_CONFIG,
    TAG_EEPROM,
    TAG_TEMPERATURE,
    TAG_RESISTOR_MONITOR,
    TAG_DOOR_STATE,
    TAG_MOTORS,
    TAG_DAC,
    TAG_COMMUNICATION,
    TAG_SERIAL_EXTRA,
    TAG_SERIAL_RS485,
    TAG_SERIAL_EXTRA_ECHO_RX,
    TAG_SERIAL_EXTRA_ECHO_HEX_RX,
    TAG_SERIAL_EXTRA_ECHO_TX,
    TAG_SERIAL_RS485_ECHO_RX,
    TAG_SERIAL_RS485_ECHO_HEX_RX,
    TAG_SERIAL_RS485_ECHO_TX,
    TAG_WARNING,
    TAG_FACTORY_MODE,
    TAG_INPUT_MANAGER,
    TAG_INPUT_MANAGER_DOOR,
    TAG_OUTPUT_MANAGER,
    TAG_BUZZER,
    TAG_SAFETY,
    TAG_SYSTEM,
    TAG_COUNT // Special value used to track the number of tags
};

// Names for the tags
extern const char* logTagNames[];

// Flags to control if certain program tags are displayed or not
extern bool enabledTags[];

// Layout structure for aligned output
struct logLayout {
    uint8_t levelColumnEnd;
    uint8_t tagColumnEnd;
};

// Enhanced logging structure
typedef struct {
    char     boot_session[37];  // UUID generated at boot
    uint64_t timestamp_us;      // Microseconds since boot
    uint32_t sequence;          // Incrementing sequence number
    uint8_t  level;             // Log level
    uint8_t  tag;               // Log tag
    char     message[512];      // Log message (user requested 512 bytes)
    char     version[16];       // Firmware version
} enhanced_log_t;

// Binary frame header for protocol output
#pragma pack(push, 1)
typedef struct {
    uint8_t  protocol_version;
    uint8_t  boot_id[16];
    uint64_t timestamp_us;
    uint32_t sequence;
    uint8_t  level;
    uint8_t  tag;
    uint8_t  fw_major;
    uint8_t  fw_minor;
    uint8_t  fw_patch;
    uint16_t msg_len;
} log_frame_header_t;
#pragma pack(pop)

// Enhanced logging modes
enum logOutputMode {
    LOG_OUTPUT_HUMAN,   // Current human-readable format
    LOG_OUTPUT_BINARY   // Binary protocol format
};

// Configuration
extern logOutputMode currentLogOutputMode;

// Logger class for consistent interface
class Logger {
public:
    Logger();

    // Initialization
    void init();

    // Utility functions
    void formatByteBinary(uint8_t byte, bool reversed, char* buffer);
    uint64_t getMicrosecondsSinceBoot();
    const char* getBootSessionId();
    uint32_t getLogSequence();

    // Configuration
    void setLogOutputMode(logOutputMode mode);

private:
    // Internal implementation functions (not exposed)
    logLayout calculateLogLayout();
};

extern Logger logger;

// Internal functions needed by macros - these remain global for macro compatibility
void logMessagefWithFlag(logTag tag, logLevel level, bool print_newline, const char* message, ...);
void logMessagefContinue(logTag tag, logLevel level, bool print_newline, const char* message, ...);

// Convenience macros for common log levels (now using enhanced logging)
#define LOG_E(tag, msg, ...) logMessagefWithFlag(tag, LOG_ERROR, true, msg, ##__VA_ARGS__)
#define LOG_W(tag, msg, ...) logMessagefWithFlag(tag, LOG_WARNING, true, msg, ##__VA_ARGS__)
#define LOG_I(tag, msg, ...) logMessagefWithFlag(tag, LOG_INFO, true, msg, ##__VA_ARGS__)
#define LOG_D(tag, msg, ...) logMessagefWithFlag(tag, LOG_DEBUG, true, msg, ##__VA_ARGS__)

// Convenience macros without println (for continuation logging)
#define LOG_E_NO_LN(tag, msg, ...) logMessagefWithFlag(tag, LOG_ERROR, false, msg, ##__VA_ARGS__)
#define LOG_W_NO_LN(tag, msg, ...) logMessagefWithFlag(tag, LOG_WARNING, false, msg, ##__VA_ARGS__)
#define LOG_I_NO_LN(tag, msg, ...) logMessagefWithFlag(tag, LOG_INFO, false, msg, ##__VA_ARGS__)
#define LOG_D_NO_LN(tag, msg, ...) logMessagefWithFlag(tag, LOG_DEBUG, false, msg, ##__VA_ARGS__)

// Convenience macros for continuation logging (no headers in human mode)
#define LOG_E_CONTINUE(tag, msg, ...) logMessagefContinue(tag, LOG_ERROR, true, msg, ##__VA_ARGS__)
#define LOG_W_CONTINUE(tag, msg, ...) logMessagefContinue(tag, LOG_WARNING, true, msg, ##__VA_ARGS__)
#define LOG_I_CONTINUE(tag, msg, ...) logMessagefContinue(tag, LOG_INFO, true, msg, ##__VA_ARGS__)
#define LOG_D_CONTINUE(tag, msg, ...) logMessagefContinue(tag, LOG_DEBUG, true, msg, ##__VA_ARGS__)

// Convenience macros for continuation logging without newline
#define LOG_E_CONTINUE_NO_LN(tag, msg, ...) logMessagefContinue(tag, LOG_ERROR, false, msg, ##__VA_ARGS__)
#define LOG_W_CONTINUE_NO_LN(tag, msg, ...) logMessagefContinue(tag, LOG_WARNING, false, msg, ##__VA_ARGS__)
#define LOG_I_CONTINUE_NO_LN(tag, msg, ...) logMessagefContinue(tag, LOG_INFO, false, msg, ##__VA_ARGS__)
#define LOG_D_CONTINUE_NO_LN(tag, msg, ...) logMessagefContinue(tag, LOG_DEBUG, false, msg, ##__VA_ARGS__)

// Enhanced logging function (now used by the standard LOG_* macros)

// Internal functions for binary protocol
void sendLogViaSerial(const enhanced_log_t* log);
uint16_t crc16Ccitt(const uint8_t* data, size_t len);
void sendByteEscaped(uint8_t byte);
void sendBufferEscaped(const uint8_t* buf, size_t len);
void parseFirmwareVersion(uint8_t* major, uint8_t* minor, uint8_t* patch);

// Binary protocol functions (matching example implementation)
void sendBinaryLog(const enhanced_log_t* log);

#endif // LOGGER_H
