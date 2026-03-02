#include "Logger.h"
#include "../config/Definitions.h"
#include <limits.h>
#include <string.h>
#include <stdio.h>

// Names for the log levels
const char* logLevelNames[] = {
    "ERROR",
    "WARNG",
    "INFO",
    "DEBUG"
};

// Names for the tags
const char* logTagNames[] = {
    "CONFIG",
    "EEPROM",
    "TEMPERATURE",
    "RESISTOR MONITOR",
    "DOOR STATE",
    "MOTORS",
    "DAC",
    "COMMUNICATION",
    "SERIAL EXTRA",
    "SERIAL RS485",
    "EXTRA ECHO RX",
    "EXTRA ECHO HEX RX",
    "EXTRA ECHO TX",
    "RS485 ECHO RX",
    "RS485 ECHO HEX RX",
    "RS485 ECHO TX",
    "WARNING",
    "FACTORY MODE",
    "INPUT MANAGER",
    "INPUT MANAGER DOOR",
    "OUTPUT MANAGER",
    "BUZZER",
    "SAFETY",
    "SYSTEM"
};

// Flags to control if certain program tags are displayed or not
bool enabledTags[TAG_COUNT] = {
    true,  // TAG_CONFIG
    true,  // TAG_EEPROM
    true,  // TAG_TEMPERATURE
    true,  // TAG_RESISTOR_MONITOR
    true,  // TAG_DOOR_STATE
    false, // TAG_MOTORS
    false, // TAG_DAC
    true,  // TAG_COMMUNICATION
    false, // TAG_SERIAL_EXTRA
    false, // TAG_SERIAL_RS485
    false, // TAG_SERIAL_EXTRA_ECHO_RX
    false, // TAG_SERIAL_EXTRA_ECHO_HEX_RX
    false, // TAG_SERIAL_EXTRA_ECHO_TX
    false, // TAG_SERIAL_RS485_ECHO_RX
    false, // TAG_SERIAL_RS485_ECHO_HEX_RX
    false, // TAG_SERIAL_RS485_ECHO_TX
    true,  // TAG_WARNING
    true,  // TAG_FACTORY_MODE
    true,  // TAG_INPUT_MANAGER
    true,  // TAG_INPUT_MANAGER_DOOR
    false, // TAG_OUTPUT_MANAGER
    false, // TAG_BUZZER
    true,  // TAG_SAFETY
    true   // TAG_SYSTEM
};

logLayout calculateLogLayout()
{
    logLayout layout;

    // Find the max length of the level name
    uint8_t maxLevelLength = 0;

    for (uint8_t i = 0; i < 4; i++)
    {
        uint8_t length = strlen(logLevelNames[i]);

        if (length > maxLevelLength)
        {
            maxLevelLength = length;
        }
    }
    // Find max length of tag name
    uint8_t maxTagLength = 0;

    for (uint8_t i = 0; i < TAG_COUNT; i++)
    {
        uint8_t length = strlen(logTagNames[i]);

        if (length > maxTagLength)
        {
            maxTagLength = length;
        }
    }
    // Calculate column positions (adding 3 for "[" + "]" + " ")
    layout.levelColumnEnd = maxLevelLength + 3;
    layout.tagColumnEnd = layout.levelColumnEnd + maxTagLength + 3;

    return layout;
}

// Enhanced logging state
static char g_boot_session_id[37] = {0};
static uint32_t g_sequence = 0;
static uint8_t g_boot_session_uuid[16] = {0};
logOutputMode currentLogOutputMode = LOG_OUTPUT_HUMAN;

// Enhanced logging functions
uint64_t getMicrosecondsSinceBoot()
{
    return (uint64_t)micros();
}

const char* getBootSessionId()
{
    return g_boot_session_id;
}

uint32_t getLogSequence()
{
    return g_sequence;
}

void setLogOutputMode(logOutputMode mode)
{
    currentLogOutputMode = mode;
}

// Generate uuid v4 in binary format
static void generateUuidV4Binary(uint8_t out[16])
{
    randomSeed((uint32_t)micros() ^ (uint32_t)millis());

    for (uint8_t i = 0; i < 16; i++)
    {
        out[i] = (uint8_t)random(0, 256);
    }

    out[6] = (out[6] & 0x0F) | 0x40; // Version 4
    out[8] = (out[8] & 0x3F) | 0x80; // Variant 10
}

// Convert binary uuid to string
static void uuidBinaryToString(const uint8_t uuid[16], char out[37])
{
    static const char* hex = "0123456789abcdef";

    uint8_t p = 0;

    for (uint8_t i = 0; i < 16; i++)
    {
        out[p++] = hex[(uuid[i] >> 4) & 0x0F];
        out[p++] = hex[(uuid[i]     ) & 0x0F];

        if ((i == 3) || (i == 5) || (i == 7) || (i == 9))
        {
            out[p++] = '-';
        }
    }

    out[36] = '\0';
}

// Initialize enhanced logging
void initLogging()
{
    generateUuidV4Binary(g_boot_session_uuid);
    uuidBinaryToString(g_boot_session_uuid, g_boot_session_id);
    g_sequence = 0;
    // Use the logging system consistently for both modes
    logMessagefWithFlag(TAG_SYSTEM, LOG_INFO, true, "logging started session=%s proto=%u fw=%s", g_boot_session_id, LOG_PROTOCOL_VERSION, FIRMWARE_VERSION);
}

// Enhanced logging function with flag for println control
void logMessagefWithFlag(logTag tag, logLevel level, bool print_newline, const char* message, ...)
{
    // Skip if level is too verbose for current settings
    if (level > CURRENT_LOG_LEVEL)
    {
        return;
    }
    // Skip if this tag is disabled
    if (!enabledTags[tag])
    {
        return;
    }
    // Create buffer for formatted message (512 bytes for user message)
    char buffer[512];
    // Format the message
    va_list args;
    va_start(args, message);
    vsnprintf(buffer, sizeof(buffer), message, args);
    va_end(args);
    // Check if we should use binary protocol
    if (currentLogOutputMode == LOG_OUTPUT_BINARY)
    {
        // Create enhanced log structure for binary transmission
        enhanced_log_t log;
        strncpy(log.boot_session, g_boot_session_id, sizeof(log.boot_session) - 1);
        log.boot_session[sizeof(log.boot_session) - 1] = '\0';
        log.timestamp_us = getMicrosecondsSinceBoot();
        log.sequence = g_sequence++;
        log.level = level;
        log.tag = tag;
        strncpy(log.message, buffer, sizeof(log.message) - 1);
        log.message[sizeof(log.message) - 1] = '\0';
        strncpy(log.version, FIRMWARE_VERSION, sizeof(log.version) - 1);
        log.version[sizeof(log.version) - 1] = '\0';

        sendBinaryLog(&log);
        return;
    }
    // Human-readable format (existing code but without println)

    // Get layout info once
    static logLayout layout = calculateLogLayout();
    // Add timestamp and sequence for enhanced human format
    debugSerial.print("[");
    unsigned long timestamp_ms = (unsigned long)(getMicrosecondsSinceBoot() / 1000);
    // Zero-pad timestamp to 9 digits for visual alignment
    if (timestamp_ms < 100000000UL)
    {
        if (timestamp_ms < 10000000UL)
        {
            if (timestamp_ms < 1000000UL)
            {
                if (timestamp_ms < 100000UL)
                {
                    if (timestamp_ms < 10000UL)
                    {
                        if (timestamp_ms < 1000UL)
                        {
                            if (timestamp_ms < 100UL)
                            {
                                if (timestamp_ms < 10UL)
                                {
                                    debugSerial.print("00000000");
                                }
                                else
                                {
                                    debugSerial.print("0000000");
                                }
                            }
                            else
                            {
                                debugSerial.print("000000");
                            }
                        }
                        else
                        {
                            debugSerial.print("00000");
                        }
                    }
                    else
                    {
                        debugSerial.print("0000");
                    }
                }
                else
                {
                    debugSerial.print("000");
                }
            }
            else
            {
                debugSerial.print("00");
            }
        }
        else
        {
            debugSerial.print("0");
        }
    }
    debugSerial.print(timestamp_ms);
    debugSerial.print("ms]");

    debugSerial.print("[");
    debugSerial.print(logLevelNames[level]);
    debugSerial.print("]");
    // Add padding after level to align tag column
    uint8_t levelLength = strlen(logLevelNames[level]) + 2; // +2 for brackets

    for (uint8_t i = levelLength; i < layout.levelColumnEnd; i++)
    {
        debugSerial.print(" ");
    }
    // Print tag with brackets
    debugSerial.print("[");
    debugSerial.print(logTagNames[tag]);
    debugSerial.print("]");
    // Add padding after tag to align message column
    uint8_t tagLength = strlen(logTagNames[tag]) + 2; // +2 for brackets

    for (uint8_t i = tagLength; i < (layout.tagColumnEnd - layout.levelColumnEnd); i++)
    {
        debugSerial.print(" ");
    }
    // Add sequence number and session info
    debugSerial.print("[#");

    uint32_t current_sequence = g_sequence++;
    // Zero-pad sequence number to 5 digits for visual alignment
    if (current_sequence < 10000UL)
    {
        if (current_sequence < 1000UL)
        {
            if (current_sequence < 100UL)
            {
                if (current_sequence < 10UL)
                {
                    debugSerial.print("0000");
                }
                else
                {
                    debugSerial.print("000");
                }
            }
            else
            {
                debugSerial.print("00");
            }
        }
        else
        {
            debugSerial.print("0");
        }
    }
    debugSerial.print(current_sequence); debugSerial.print("] ");

    if (print_newline)
    {
        debugSerial.println(buffer);
    }
    else
    {
        debugSerial.print(buffer);
    }
}

// Enhanced logging function for continuation (no headers in human mode, full message in binary mode)
void logMessagefContinue(logTag tag, logLevel level, bool print_newline, const char* message, ...)
{
    // Skip if level is too verbose for current settings
    if (level > CURRENT_LOG_LEVEL)
    {
        return;
    }
    // Skip if this tag is disabled
    if (!enabledTags[tag])
    {
        return;
    }
    // Create buffer for formatted message (512 bytes for user message)
    char buffer[512];
    // Format the message
    va_list args;
    va_start(args, message);
    vsnprintf(buffer, sizeof(buffer), message, args);
    va_end(args);
    // Check if we should use binary protocol
    if (currentLogOutputMode == LOG_OUTPUT_BINARY)
    {
        // In binary mode, send full structured message like normal
        enhanced_log_t log;
        strncpy(log.boot_session, g_boot_session_id, sizeof(log.boot_session) - 1);
        log.boot_session[sizeof(log.boot_session) - 1] = '\0';
        log.timestamp_us = getMicrosecondsSinceBoot();
        log.sequence = g_sequence++;
        log.level = level;
        log.tag = tag;
        strncpy(log.message, buffer, sizeof(log.message) - 1);
        log.message[sizeof(log.message) - 1] = '\0';
        strncpy(log.version, FIRMWARE_VERSION, sizeof(log.version) - 1);
        log.version[sizeof(log.version) - 1] = '\0';

        sendBinaryLog(&log);
        return;
    }
    // Human-readable format - only print the message content, no headers
    if (print_newline)
    {
        debugSerial.println(buffer);
    }
    else
    {
        debugSerial.print(buffer);
    }
}

// Crc-16 ccitt implementation (from example)
uint16_t crc16Ccitt(const uint8_t* data, size_t len)
{
    uint16_t crc = 0xFFFF;

    for (size_t i = 0; i < len; i++)
    {
        crc ^= (uint16_t)data[i] << 8;

        for (uint8_t j = 0; j < 8; j++)
        {
            if (crc & 0x8000)
            {
                crc = (crc << 1) ^ 0x1021;
            }
            else
            {
                crc = crc << 1;
            }
        }
    }

    return crc;
}

// Send byte with slip escaping (from example)
void sendByteEscaped(uint8_t byte)
{
    if (byte == FRAME_START_BYTE || byte == FRAME_ESCAPE_BYTE)
    {
        debugSerial.write(FRAME_ESCAPE_BYTE);
        debugSerial.write(byte ^ FRAME_XOR_MASK);
    }
    else
    {
        debugSerial.write(byte);
    }
}

// Send buffer with escaping (from example)
void sendBufferEscaped(const uint8_t* buf, size_t len)
{
    for (size_t i = 0; i < len; i++)
    {
        sendByteEscaped(buf[i]);
    }
}

// Parse firmware version string to components (from example)
void parseFirmwareVersion(uint8_t* major, uint8_t* minor, uint8_t* patch)
{
    *major = 0;
    *minor = 0;
    *patch = 0;
    // Parse firmware_version like "1.2.4"
    const char* ver = FIRMWARE_VERSION;

    if (ver)
    {
        sscanf(ver, "%hhu.%hhu.%hhu", major, minor, patch);
    }
}

// Binary log transmission function (from example, adapted for our structures)
void sendBinaryLog(const enhanced_log_t* log)
{
    // Build frame header
    log_frame_header_t header;
    memset(&header, 0, sizeof(header));

    header.protocol_version = LOG_PROTOCOL_VERSION;
    memcpy(header.boot_id, g_boot_session_uuid, 16);
    header.timestamp_us = log->timestamp_us;
    header.sequence = log->sequence;
    header.level = log->level;
    header.tag = log->tag;

    parseFirmwareVersion(&header.fw_major, &header.fw_minor, &header.fw_patch);
    // Limit message length
    size_t msg_len = strlen(log->message);

    if (msg_len > sizeof(log->message)) msg_len = sizeof(log->message);

    header.msg_len = (uint16_t)msg_len;
    // Calculate crc over header + message
    uint8_t temp_buffer[sizeof(header) + 512];
    memcpy(temp_buffer, &header, sizeof(header));
    memcpy(temp_buffer + sizeof(header), log->message, msg_len);
    uint16_t crc = crc16Ccitt(temp_buffer, sizeof(header) + msg_len);
    // Send frame

    // 1. Start byte (unescaped)
    debugSerial.write(FRAME_START_BYTE);
    // 2. Header (escaped)
    sendBufferEscaped((uint8_t*)&header, sizeof(header));
    // 3. Message (escaped)
    sendBufferEscaped((uint8_t*)log->message, msg_len);
    // 4. Crc (escaped, little-endian)
    sendByteEscaped(crc & 0xFF);
    sendByteEscaped((crc >> 8) & 0xFF);
    // 5. End with another start byte (marks end and can start next frame)
    debugSerial.write(FRAME_START_BYTE);
    // Flush to ensure immediate transmission
    debugSerial.flush();
}

// Wrapper function for compatibility - binary/human switching is now handled in logmessagef
void sendLogViaSerial(const enhanced_log_t* log)
{
    if (currentLogOutputMode == LOG_OUTPUT_BINARY)
    {
        sendBinaryLog(log);
    }
    // Human mode is handled directly in logmessagef
}

Logger logger;

Logger::Logger()
{
}

// Instance method implementations
void Logger::init()
{
    initLogging();
}

void Logger::formatByteBinary(uint8_t byte, bool reversed, char* buffer)
{
    ::formatByteBinary(byte, reversed, buffer);
}

uint64_t Logger::getMicrosecondsSinceBoot()
{
    return ::getMicrosecondsSinceBoot();
}

const char* Logger::getBootSessionId()
{
    return ::getBootSessionId();
}

uint32_t Logger::getLogSequence()
{
    return ::getLogSequence();
}

void Logger::setLogOutputMode(logOutputMode mode)
{
    ::setLogOutputMode(mode);
}

logLayout Logger::calculateLogLayout()
{
    return ::calculateLogLayout();
}
