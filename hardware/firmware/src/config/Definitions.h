
#ifndef DefinitionsFeralBoard_h
#define DefinitionsFeralBoard_h

#include <Arduino.h>

#include "Wire.h"
#include "SPI.h"
#include "MCP4725.h"
#include "Adafruit_MAX31856.h"
#include "EEPROM.h"

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/**********************************************************************************************************/

//  Temperature simulation defines

//  #define SIMULATE_TEMPERATURE_FOR_DEBUG

    #define SIMULATED_TEMPERATURE_CHANGE                            1.0f
    #define MIN_SIMULATED_TEMPERATURE                               20.0f
    #define MAX_SIMULATED_TEMPERATURE                               400.0f

    #define DELAY_BETWEEN_SIMULATED_TEMPERATURE_READINGS            5000

/**********************************************************************************************************/

#define SERIAL_DOOR_STATE_PRINT_DELAY                               5000
#define SERIAL_INPUT_STATE_PRINT_DELAY                              5000
#define SERIAL_TEMPERATURE_PRINT_DELAY                              1000
#define SERIAL_DEBUG_COMMUNICATION_TIMEOUT                          30
#define SERIAL_EXTRA_COMMUNICATION_TIMEOUT                          30
#define SERIAL_RS485_COMMUNICATION_TIMEOUT                          30
#define SERIAL_TIMEOUT_MS                                           30
#define SERIAL_DEBUG_BAUD_RATE                                      921600
#define SERIAL_EXTRA_BAUD_RATE                                      9600
#define SERIAL_RS485_BAUD_RATE                                      9600

#define debugSerial                                                 Serial
#define extraSerial                                                 Serial1
#define rs485Serial                                                 Serial3

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Pinout identification
#define UART0_DEFAULT_TX_PIN                                        0
#define UART0_DEFAULT_RX_PIN                                        1

#define SDA_PIN                                                     2
#define SCL_PIN                                                     3

#define MOSI_DEFAULT_PIN                                            4
#define MISO_DEFAULT_PIN                                            5
#define SCK_DEFAULT_PIN                                             6
//      not used                                                    7

#define UART3_DEFAULT_TX_PIN                                        8
#define UART3_DEFAULT_RX_PIN                                        9
#define RS485_DRIVER_ENABLE_PIN                                     10

#define RELAY_CONTROLLER_SET_OUTPUTS_PIN                            11
#define RELAY_CONTROLLER_ENABLE_PIN                                 12

#define BUZZER_PIN                                                  13

#define ABRIR_CONTROLLER_IN1_PIN                                    14
#define ABRIR_CONTROLLER_IN2_PIN                                    15

//      not used                                                    16
#define COOLING_FAN_CONTROL_PIN                                     17

#define UART1_DEFAULT_TX_PIN                                        18
#define UART1_DEFAULT_RX_PIN                                        19

#define INPUTS_MUX_CHANNEL_SELECT_3_PIN                             20
#define INPUTS_MUX_CHANNEL_SELECT_2_PIN                             21
#define INPUTS_MUX_CHANNEL_SELECT_1_PIN                             22
#define INPUTS_MUX_CHANNEL_SELECT_0_PIN                             23

#define INPUTS_MUX_ENABLE_PIN                                       24
#define INPUTS_MUX_SIGNAL_PIN                                       25

#define LED_RED_SIGNAL_PIN                                          26
#define LED_BLUE_SIGNAL_PIN                                         27

#define THERMOCOUPLE_MUX_ENABLE_PIN                                 28
#define DATA_READY_THERMOCOUPLE_PIN                                 29

#define FAULT_THERMOCOUPLE_PIN                                      30

#define SSR_A_PIN                                                   31
#define SSR_B_PIN                                                   32
#define SSR_C_PIN                                                   33

#define THERMOCOUPLE_MUX_CHANNEL_SELECT_0_PIN                       34
#define THERMOCOUPLE_MUX_CHANNEL_SELECT_1_PIN                       35
#define SELECT_THERMOCOUPLE_PIN                                     36
#define STROBE_INPUT_PIN                                            37

#define FECHAR_CONTROLLER_IN1_PIN                                   38
#define FECHAR_CONTROLLER_IN2_PIN                                   39

#define RESET_PIN                                                   40

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Pinout definitions
#define SPI_CHIP_SELECTED                                           LOW
#define SPI_CHIP_DESELECTED                                         HIGH

#define RS485_DRIVER_RECEIVING                                      LOW
#define RS485_DRIVER_TRANSMITTING                                   HIGH

#define RELAY_CONTROLLER_ENABLED                                    LOW
#define RELAY_CONTROLLER_DISABLED                                   HIGH

#define RELAY_INACTIVE                                              LOW
#define RELAY_ACTIVE                                                HIGH

#define ABRIR_MOTOR_DIRECTION_1                                     LOW
#define ABRIR_MOTOR_DIRECTION_2                                     HIGH

#define MULTIPLEXER_ENABLED                                         LOW
#define MULTIPLEXER_DISABLED                                        HIGH

#define LED_ENABLED                                                 LOW
#define LED_DISABLED                                                HIGH

#define ORIGINAL_PINS_I2C                                           LOW
#define ALTERNATIVE_PINS_I2C                                        HIGH

#define ORIGINAL_PINS_EXTRA_SERIAL                                  LOW
#define ALTERNATIVE_PINS_EXTRA_SERIAL                               HIGH

#define FECHAR_MOTOR_DIRECTION_1                                    LOW
#define FECHAR_MOTOR_DIRECTION_2                                    HIGH

#define INPUT_OFF                                                   LOW
#define INPUT_ON                                                    HIGH

#define OUTPUT_OFF                                                  LOW
#define OUTPUT_ON                                                   HIGH

#define OUTPUTS_CONTROL_DELAYED                                     LOW
#define OUTPUTS_CONTROL_IMMEDIATE                                   HIGH

#define COOLING_FAN_OFF                                             LOW
#define COOLING_FAN_ON                                              HIGH

#define RESISTOR_POWER_OFF                                          LOW
#define RESISTOR_POWER_ON                                           HIGH

#define LOCK_TYPE_MANUAL                                            LOW
#define LOCK_TYPE_ELECTRIC                                          HIGH

#define LAVAGEM_MODULE_NOT_PRESENT                                  LOW
#define LAVAGEM_MODULE_PRESENT                                      HIGH

#define OVEN_POSITION_BTM                                           LOW
#define OVEN_POSITION_TOP                                           HIGH

#define EXTRACTOR_NOT_PRESENT                                       LOW
#define EXTRACTOR_PRESENT                                           HIGH

#define CONNDENSER_NOT_PRESENT                                      LOW
#define CONNDENSER_PRESENT                                          HIGH

// Examples for oven model possibilities

// bit 0 - lock type | bit 1 - washing | bit 2 - position | bit 3 - extractor | bit 4 - condenser | bit 5 to 7 - not used
#define OVEN_BTM_LAVAGEM_OFF_MANUAL                                 0b00000000
#define OVEN_BTM_LAVAGEM_OFF_ELECTRIC                               0b00000001
#define OVEN_BTM_LAVAGEM_ON_MANUAL                                  0b00000010
#define OVEN_BTM_LAVAGEM_ON_ELECTRIC                                0b00000011
#define OVEN_TOP_LAVAGEM_OFF_MANUAL                                 0b00000100
#define OVEN_TOP_LAVAGEM_OFF_ELECTRIC                               0b00000101
#define OVEN_TOP_LAVAGEM_ON_MANUAL                                  0b00000110
#define OVEN_TOP_LAVAGEM_ON_ELECTRIC                                0b00000111

#define DEFAULT_OVEN_MODEL                                          0b00000011

// Other model possibilities are not yet implemented

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Communication definitions

#define REQUESTS_BUFFER_SIZE                                        11
#define RESPONSE_BUFFER_SIZE                                        41

#define RS485_REQUESTS_BUFFER_SIZE                                  11 // was 10 now 10 + 1 for checksum
#define RS485_RESPONSE_BUFFER_SIZE                                  41 // was 40 now 40 + 1 for checksum

// Requests buffer byte locations
#define OVEN_OUTPUTS_STATE_00_07_LOCATION                           0
#define OVEN_OUTPUTS_STATE_08_15_LOCATION                           1
#define OVEN_OUTPUTS_STATE_16_23_LOCATION                           2
#define OVEN_OUTPUTS_STATE_EXTRA_LOCATION                           3
#define COMMAND_OVEN_ID_LOCATION                                    4
#define COMMAND_OVEN_DT_LOCATION                                    5
#define LAVAGEM_OUTPUTS_STATE_00_04_REQUESTS_LOCATION               6
#define COMMAND_LAVAGEM_ID_LOCATION                                 7
#define COMMAND_LAVAGEM_DT_LOCATION                                 8
#define REQUESTS_ORIGIN_IDENTIFIER_LOCATION                         9
#define REQUESTS_CHECKSUM_LOCATION                                  10 // checksum location

// Responses buffer byte locations

// First 4 bytes are equal to the requests buffer byte locations
#define OVEN_INPUTS_STATE_00_07_LOCATION                            4
#define OVEN_INPUTS_STATE_08_15_LOCATION                            5
#define OVEN_TEMPERATURE_BYTE_0_LOCATION                            6
#define OVEN_TEMPERATURE_BYTE_1_LOCATION                            7
#define OVEN_TEMPERATURE_BYTE_2_LOCATION                            8
#define OVEN_TEMPERATURE_BYTE_3_LOCATION                            9
#define EXTRA_1_TEMPERATURE_BYTE_0_LOCATION                         10
#define EXTRA_1_TEMPERATURE_BYTE_1_LOCATION                         11
#define EXTRA_1_TEMPERATURE_BYTE_2_LOCATION                         12
#define EXTRA_1_TEMPERATURE_BYTE_3_LOCATION                         13
#define EXTRA_2_TEMPERATURE_BYTE_0_LOCATION                         14
#define EXTRA_2_TEMPERATURE_BYTE_1_LOCATION                         15
#define EXTRA_2_TEMPERATURE_BYTE_2_LOCATION                         16
#define EXTRA_2_TEMPERATURE_BYTE_3_LOCATION                         17
#define EXTRA_3_TEMPERATURE_BYTE_0_LOCATION                         18
#define EXTRA_3_TEMPERATURE_BYTE_1_LOCATION                         19
#define EXTRA_3_TEMPERATURE_BYTE_2_LOCATION                         20
#define EXTRA_3_TEMPERATURE_BYTE_3_LOCATION                         21
#define OVEN_PCB_TEMPERATURE_LOCATION                               22
#define OVEN_INTERNAL_ERRORS_LOCATION                               23
#define OVEN_OTHER_STATES_LOCATION                                  24
#define OVEN_MODEL_LOCATION                                         25
#define OVEN_INTERNAL_BUZZER_VOLUME_LOCATION                        26
#define OVEN_ECHO_LAST_COMMAND_LOCATION                             27
#define LAVAGEM_OUTPUTS_STATE_00_04_RESPONSE_LOCATION               28
#define LAVAGEM_INPUTS_STATE_00_03_RESPONSE_LOCATION                29
#define LAVAGEM_TEMPERATURE_BYTE_0_LOCATION                         30
#define LAVAGEM_TEMPERATURE_BYTE_1_LOCATION                         31
#define LAVAGEM_TEMPERATURE_BYTE_2_LOCATION                         32
#define LAVAGEM_TEMPERATURE_BYTE_3_LOCATION                         33
#define LAVAGEM_PCB_TEMPERATURE_LOCATION                            34
#define LAVAGEM_DETERGENT_AMOUNT_LOCATION                           35
#define LAVAGEM_INTERNAL_ERRORS_LOCATION                            36
#define LAVAGEM_OTHER_STATES_LOCATION                               37
#define LAVAGEM_ECHO_LAST_COMMAND_LOCATION                          38
#define RESPONSE_DESTINATION_IDENTIFIER_LOCATION                    39
#define RESPONSE_CHECKSUM_LOCATION                                  40 // checksum location

#define ORIGIN_SERIAL_DEBUG                                         0
#define ORIGIN_SERIAL_EXTRA                                         1
#define ORIGIN_SERIAL_RS485                                         3

#define COMMUNICATION_WARNING_TIMEOUT                               20000
#define COMMUNICATION_LAVAGEM_TIMEOUT                               20000

#define WARNING_BUZZER_INTERVAL                                     60000
#define LAVAGEM_MESSAGE_ERROR_TIMEOUT                               100

// Specific commands
#define SET_STATES_COMMAND                                          0x00
#define GET_STATES_COMMAND                                          0x01
#define RST_STATES_COMMAND                                          0x02
#define SET_INVERT_COMMAND                                          0x03
#define CLR_INVERT_COMMAND                                          0x04
#define FACTORY_MODE_COMMAND                                        0x05
#define OPEN_DOOR_COMMAND                                           0x06
#define CLOSE_DOOR_COMMAND                                          0x07
#define MOTOR_CONTROL_COMMAND                                       0x08
#define OVEN_MODEL_COMMAND                                          0x09
#define BUZZER_STRENGTH_COMMAND                                     0x0A
#define BUZZER_FREQUENCY_COMMAND                                    0x0B
#define MOTOR_SLOW_SPEED_COMMAND                                    0x0C
#define MOTOR_FAST_SPEED_COMMAND                                    0x0D
#define SET_NUMBER_THERMOCOUPLES_COMMAND                            0x0E
#define SET_LAVAGEM_BTM_STATE_COMMAND                               0x0F
#define SET_LAVAGEM_TOP_STATE_COMMAND                               0x10
#define SET_LAVAGEM_DETERGENT_AMOUNT_COMMAND                        0x11
#define TURN_OFF_FORCED_VENTILATION                                 0x12

#define INVALID_COMMAND                                             0xFE
#define UNRECOGNIZED_COMMAND                                        0xFF

// Specific command data

// When a command to motor control is sent with one of this values in the payload then a specific action will be taken regarding the electric lock
#define OPEN_MOTOR_NORMAL_DIRECTION                                 0x01
#define OPEN_MOTOR_REVERSE_DIRECTION                                0x02
#define CLOSE_MOTOR_NORMAL_DIRECTION                                0x03
#define CLOSE_MOTOR_REVERSE_DIRECTION                               0x04
#define START_LOCK_RESET                                            0x05
#define START_LOCK_REPOSITION                                       0x06

// Bit locations for the specific transmitted bytes related to the oven

// All bytes after byte 27 are not related to the oven

// byte 0 - outputs oven 00-07
#define DIRECTION_1_BIT                                             0   /* byte 0 */
#define DIRECTION_2_BIT                                             1   /* byte 0 */
#define VELOCIDADE_1_BIT                                            2   /* byte 0 */
#define VELOCIDADE_2_BIT                                            3   /* byte 0 */
#define RESISTOR_BIT                                                4   /* byte 0 */
#define VAPOUR_EXIT_BIT                                             5   /* byte 0 */
#define EXTRACTOR_BIT                                               6   /* byte 0 */
#define VAPOR_CREATION_BIT                                          7   /* byte 0 */

// byte 1 - outputs oven 08-15
//      not used                                                    0   /* byte 1 */
//      not used                                                    1   /* byte 1 */
//      not used                                                    2   /* BYTE 1 */
//      not used                                                    3   /* byte 1 */
//      not used                                                    4   /* byte 1 */
//      not used                                                    5   /* byte 1 */
//      not used                                                    6   /* byte 1 */
//      not used                                                    7   /* byte 1 */

// byte 2 - outputs oven 16-23
//      not used                                                    0   /* byte 2 */
//      not used                                                    1   /* byte 2 */
//      not used                                                    2   /* byte 2 */
//      not used                                                    3   /* byte 2 */
//      not used                                                    4   /* byte 2 */
//      not used                                                    5   /* byte 2 */
#define OVEN_ILUMINATION_BIT                                        6   /* byte 2 */
#define BUZZER_EXTERNAL_BIT                                         7   /* byte 2 */

// byte 3 - outputs extra oven
#define BUZZER_INTERNAL_BIT                                         0   /* byte 3 */
#define COOLING_FAN_BIT                                             1   /* byte 3 */
//      not used                                                    2   /* byte 3 */
//      not used                                                    3   /* byte 3 */
//      not used                                                    4   /* byte 3 */
//      not used                                                    5   /* byte 3 */
//      not used                                                    6   /* byte 3 */
//      not used                                                    7   /* byte 3 */

// byte 4 - inputs oven 00-07
#define DOOR_END_STOP_BIT                                           0   /* byte 4 */
#define ELECTRIC_PROTECTION_BIT                                     1   /* byte 4 */
#define OVEN_OVER_TEMPERATURE_BIT                                   2   /* byte 4 */
#define MOTOR_OVER_TEMPERATURE_BIT                                  3   /* byte 4 */
#define DOOR_SWITCH_LOCKED_BIT                                      4   /* byte 4 */
#define DOOR_SWITCH_LOCKING_1_BIT                                   5   /* byte 4 */
#define DOOR_SWITCH_LOCKING_2_BIT                                   6   /* byte 4 */
#define DOOR_SWITCH_TRACTION_BIT                                    7   /* byte 4 */

// byte 5 - inputs oven 08-15
//      not used                                                    0   /* byte 5 */
//      not used                                                    1   /* byte 5 */
//      not used                                                    2   /* byte 5 */
//      not used                                                    3   /* byte 5 */
//      not used                                                    4   /* byte 5 */
//      not used                                                    5   /* byte 5 */
//      not used                                                    6   /* byte 5 */
//      not used                                                    7   /* byte 5 */

// .
// .    bytes related to the thermocouple and pcb temperature readings (bytes 06 to 22)
// .

// byte 23 - oven internal errors
#define FAULT_ELECTRIC_LOCK_BIT                                     0   /* byte 23 */
#define FAULT_EEPROM_INTERNAL_BIT                                   1   /* byte 23 */
#define FAULT_MAIN_THERMOCOUPLE_OVUV_BIT                            1   /* byte 23 */
#define FAULT_FORCED_VENTILATION_BIT                                2   /* byte 23 */
#define FAULT_CONCURRENT_OUTPUTS_BIT                                3   /* byte 23 */
#define FAULT_RESISTOR_PROBLEM_BIT                                  3   /* byte 23 */
#define FAULT_MAIN_THERMOCOUPLE_BIT                                 4   /* byte 23 */
#define FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT                       5   /* byte 23 */
#define FAULT_MAIN_THERMOCOUPLE_OPEN_BIT                            6   /* byte 23 */
#define FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT                      7   /* byte 23 */

// byte 24 - oven other states
#define FACTORY_MODE_STATE_BIT                                      0   /* byte 24 */
#define OPENING_MOTOR_NORMAL_STATE_BIT                              1   /* byte 24 */
#define OPENING_MOTOR_REVERSE_STATE_BIT                             2   /* byte 24 */
#define CLOSING_MOTOR_NORMAL_STATE_BIT                              3   /* byte 24 */
#define CLOSING_MOTOR_REVERSE_STATE_BIT                             4   /* byte 24 */
#define DOOR_REPOSITION_IN_PROGRESS_BIT                             5   /* byte 24 */
#define DOOR_DEBOUNCED_STATE_BIT_1                                  6   /* byte 24 */
#define DOOR_DEBOUNCED_STATE_BIT_2                                  7   /* byte 24 */

// byte 25 - oven model
#define OVEN_MODEL_LOCK_TYPE_BIT                                    0   /* byte 25 */
#define OVEN_MODEL_WASHING_BIT                                      1   /* byte 25 */
#define OVEN_MODEL_POSITION_BIT                                     2   /* byte 25 */
#define OVEN_EXTRACTOR_BIT                                          3   /* byte 25 */
#define OVEN_CONDENSER_BIT                                          4   /* byte 25 */
//      not used                                                    5   /* byte 25 */
//      not used                                                    6   /* byte 25 */
//      not used                                                    7   /* byte 25 */

// byte 26 - oven internal buzzer volume

// byte 27 - oven echo last command

// byte 36 - lavagem internal errors
#define FAULT_LAVAGEM_COMMUNICATION_BIT                             0   /* byte 36 */
#define FAULT_EEPROM_INTERNAL_BIT                                   1   /* byte 36 */
#define FAULT_MAIN_THERMOCOUPLE_OVUV_BIT                            1   /* byte 36 */
//      not used                                                    2   /* byte 36 */
#define FAULT_CONCURRENT_OUTPUTS_BIT                                3   /* byte 36 */
#define FAULT_MAIN_THERMOCOUPLE_BIT                                 4   /* byte 36 */
#define FAULT_MAIN_THERMOCOUPLE_HIGH_TEMP_BIT                       5   /* byte 36 */
#define FAULT_MAIN_THERMOCOUPLE_OPEN_BIT                            6   /* byte 36 */
#define FAULT_MAIN_THERMOCOUPLE_STUCK_TEMP_BIT                      7   /* byte 36 */

// byte 37 - lavagem other states
#define FACTORY_MODE_STATE_BIT                                      0   /* byte 37 */
#define LAVAGEM_TOP_IS_ACTIVE_BIT                                   1   /* byte 37 */
#define LAVAGEM_BTM_IS_ACTIVE_BIT                                   2   /* byte 37 */
//      not used                                                    3   /* byte 37 */
//      not used                                                    4   /* byte 37 */
//      not used                                                    5   /* byte 37 */
//      not used                                                    6   /* byte 37 */
//      not used                                                    7   /* byte 37 */

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Motor definitions

#define MOTORS_OFF                                                  0
#define MOTORS_ON                                                   1

// Motor speed options
#define MOTORS_OFF_SPEED                                            0
#define DEFAULT_FAST_MOTOR_SPEED                                    255
#define DEFAULT_SLOW_MOTOR_SPEED                                    200

// Electric lock definitions

// Truth table for the possible electric door inputs
#define MASK_DOOR_OPEN_ELECTRIC                                     0b01010000
#define MASK_DOOR_INTERMEDIATE_ELECTRIC                             0b00100000
#define MASK_DOOR_CLOSED_ELECTRIC                                   0b00000000
#define MASK_DOOR_UNKNOWN_ELECTRIC                                  0b11111111

// Used to test only the specific inputs that are related to the electric lock and check if the door is in one of the four possible states specified above
#define DOOR_STATE_MASK                                             0b11110000

// Delay between the tests that are run on the specific inputs related to the electric lock and apply the masks specified above
#define DELAY_BETWEEN_DOOR_READINGS                                 20

// Debounced dorr states used in bit 6 & 7 of transmission message byte 25 - oven other states
#define DEBOUNCED_DOOR_STATE_UNKNOWN                                0b00000000 /* bit 6 & 7 */
#define DEBOUNCED_DOOR_STATE_OPEN                                   0b01000000 /* bit 6 & 7 */
#define DEBOUNCED_DOOR_STATE_INTERMEDIATE                           0b10000000 /* bit 6 & 7 */
#define DEBOUNCED_DOOR_STATE_CLOSED                                 0b11000000 /* bit 6 & 7 */

// Used to mask the debounced door states specified above into the byte 25 - oven other states of the transmission message
#define DEBOUNCED_DOOR_STATE_MASK                                   0b00111111 /* bit 6 & 7 */

// With manual lock when the end stop is not pressed (door is open) there is 24VAC on the input -> digital signal in the input state is a 1 when door closed and 0 when door open
#define DOOR_CLOSED_MANUAL                                          0x01
#define DOOR_OPEN_MANUAL                                            0x00

// With electric lock when the end stop is not pressed (door is open) there is 0VDC on the input -> digital signal in the input state is a 0 when door closed and 1 when door open
#define DOOR_CLOSED_ELECTRIC                                        0x00
#define DOOR_OPEN_ELECTRIC                                          0x01

// Diverse door states used for the algorithm to decide how to actuate the motors and to determine when errors ocurr in the electric lock
#define DOOR_OPENING_ELECTRIC                                       0x02
#define DOOR_OPENING_REVERSE_INTERVAL                               0x03
#define DOOR_OPENING_REVERSE_ELECTRIC                               0x04
#define DOOR_INTERMEDIATE_ELECTRIC                                  0x05
#define DOOR_CLOSING_ELECTRIC                                       0x06
#define DOOR_CLOSING_REVERSE_INTERVAL                               0x07
#define DOOR_CLOSING_REVERSE_ELECTRIC                               0x08
#define DOOR_SOFT_RESET_CLOSING_ROTATION                            0x09
#define DOOR_SOFT_RESET_CLOSING_REVERSE_ROTATION                    0x0A
#define DOOR_SOFT_RESET_OPENING_ROTATION                            0x0B
#define DOOR_ALREADY_CLOSED_ELECTRIC                                0xFE
#define DOOR_UNKNOWN_STATE_ELECTRIC                                 0xFE
#define DOOR_ERROR_STATE_ELECTRIC                                   0xFF

// Defines related to door error detection and to the algorithm that does the door reposition
#define DOOR_MOVEMENT_ERROR_DELAY                                   3000
#define DOOR_SECOND_TRY_TIMEOUT                                     5000
#define DOOR_REPOSITION_OPENING_DELAY                               2000
#define DOOR_REPOSITION_OPENING_TRIES                               4
#define DOOR_REPOSITION_CLOSING_DELAY                               1000
#define DOOR_REPOSITION_CLOSING_TRIES                               4
#define DOOR_CLOSING_DELAY                                          750
#define DOOR_CLOSING_INTERVAL_DELAY                                 100
#define DOOR_SOFT_RESET_ROTATION_DELAY                              500
#define DOOR_SOFT_RESET_CLOSING_REVERSE_ROTATION_DELAY              1000

// If a valid door state is not detected after a predifined amount of times then the door reposition algorithm is automatically started
#define LOCK_REPOSITION_TRIGGER                                     200

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Misc definitions
#define NO_VALUE                                                    0
#define RESET_VALUE                                                 0
#define RESET_BUFFER                                                0

#define PRINT_BYTE_NORMAL                                           0
#define PRINT_BYTE_REVERSED                                         1

#define STROBE_TOGGLE_INTERVAL                                      25

#define STARTING_DELAY                                              500

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Motor speed level definitions
#define DAC_ADRESS                                                  0x60

#define DAC_OUTPUT_STEP                                             0.5f

#define MOTOR_SPEED_LEVEL_OFF                                       0x00
#define MOTOR_SPEED_LEVEL_1                                         0x01
#define MOTOR_SPEED_LEVEL_2                                         0x02
#define MOTOR_SPEED_LEVEL_3                                         0x03
#define MOTOR_SPEED_LEVEL_4                                         0x04
#define MOTOR_SPEED_LEVEL_5                                         0x05
#define MOTOR_SPEED_LEVEL_6                                         0x06
#define MOTOR_SPEED_LEVEL_7                                         0x07
#define MOTOR_SPEED_LEVEL_8                                         0x08
#define MOTOR_SPEED_LEVEL_9                                         0x09
#define MOTOR_SPEED_LEVEL_10                                        0x0A

extern MCP4725 dac;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Relay control definitions
#define NUMBER_SHIFT_REGISTERS                                      3

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Inputs multiplexer definitions
#define INPUTS_MUX_CHANNEL_0_SELECTED                               0b00000000
#define INPUTS_MUX_CHANNEL_1_SELECTED                               0b00000001
#define INPUTS_MUX_CHANNEL_2_SELECTED                               0b00000010
#define INPUTS_MUX_CHANNEL_3_SELECTED                               0b00000011
#define INPUTS_MUX_CHANNEL_4_SELECTED                               0b00000100
#define INPUTS_MUX_CHANNEL_5_SELECTED                               0b00000101
#define INPUTS_MUX_CHANNEL_6_SELECTED                               0b00000110
#define INPUTS_MUX_CHANNEL_7_SELECTED                               0b00000111
#define INPUTS_MUX_CHANNEL_8_SELECTED                               0b00001000
#define INPUTS_MUX_CHANNEL_9_SELECTED                               0b00001001
#define INPUTS_MUX_CHANNEL_10_SELECTED                              0b00001010
#define INPUTS_MUX_CHANNEL_11_SELECTED                              0b00001011
#define INPUTS_MUX_CHANNEL_12_SELECTED                              0b00001100
#define INPUTS_MUX_CHANNEL_13_SELECTED                              0b00001101
#define INPUTS_MUX_CHANNEL_14_SELECTED                              0b00001110
#define INPUTS_MUX_CHANNEL_15_SELECTED                              0b00001111

#define NUMBER_INPUTS_MULTIPLEXER_CHANNELS_ACTIVE                   16

// Thermocouple multiplexer definitions
#define TC_MUX_CHANNEL_0_SELECTED                                   0b00000000
#define TC_MUX_CHANNEL_1_SELECTED                                   0b00000001
#define TC_MUX_CHANNEL_2_SELECTED                                   0b00000010
#define TC_MUX_CHANNEL_3_SELECTED                                   0b00000011

#define NUMBER_TC_MULTIPLEXER_CHANNELS_ACTIVE                       4

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*
    INPUTS
*/
#define DELAY_BETWEEN_READING_INPUTS                                250
#define DELAY_BETWEEN_READING_DOOR_INPUTS                           20
#define DELAY_BETWEEN_READING_INPUT                                 1

#define ERROR_INPUTS_DEBOUNCE                                       1000

#define NUMBER_INPUTS_TO_READ                                       4

#define OVEN_INPUTS_STATE_00_07                                     0
#define OVEN_INPUTS_STATE_08_15                                     1

typedef union
{
    // Byte array that represents the integer value of the input state
    byte byteArray[sizeof(uint16_t)] = { 0b00000000 , 0b00000000 };

    // Integer value for the input state
    uint16_t intValue;
}
inputsStateUnion;

// Reads all the channels of the multiplexer and stores the values in the inputState structure
void getInputs();

// Reads a specific multiplexer channel and returns the value as a boolen
bool getInputs(uint16_t channelToRead);

// Outputs
#define OUTPUTS_STATE_CHANGE_DELAY                                  1000 // Delay between the enabling and disabling of the most important outputs (motor speed / motor direction / resistor) */

#define OVEN_OUTPUTS_STATE_00_07                                    0
#define OVEN_OUTPUTS_STATE_08_15                                    1
#define OVEN_OUTPUTS_STATE_16_23                                    2
#define OVEN_OUTPUTS_STATE_EXTRA                                    3
#define OVEN_OUTPUTS_RESISTOR_POWER                                 4

#define NUMBER_OF_OUTPUTS_CHANNELS                                  4

#define OUTPUT_REFRESH_INTERVAL                                     10

typedef union
{
    // Byte array that represents the integer value of the output state
    byte byteArray[sizeof(uint32_t)] = { 0b00000000 , 0b00000000 , 0b00000000 , 0b00000000 }; // Because there are only 3 shift registers the byte number 3 is used for the extra outputs

    // Integer value for the output state
    uint32_t intValue;
}
outputStateUnion;

#define MINIMUM_DUTY_CYCLE_VALUE                                    0.0f
#define MAXIMUM_DUTY_CYCLE_VALUE                                    100.0f

#define RESISTOR_PWM_PERIOD                                         1000 // The PWM applied to the solid state relay has 1Hz frequency

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define DELAY_BETWEEN_THERMOCOUPLE_READINGS                         1000 // This delay is the interval in which no reading is being done by the thermocouple converter and the thermocouple multiplexer outputs are deactivated
#define DELAY_BETWEEN_DISPLAY_READINGS                              2000
#define DELAY_BETWEEN_REINITIALIZATION                              2000
#define NUMBER_THERMOCOUPLES_ON_BOARD                               4
#define DEFAULT_THERMOCOUPLE_AMOUNT                                 1

#define NUMBER_OF_SAMPLES_TO_AVERAGE                                10

#define MAIN_THERMOCOUPLE_SELECTED                                  0
#define EXTRA_1_THERMOCOUPLE_SELECTED                               1
#define EXTRA_2_THERMOCOUPLE_SELECTED                               2
#define EXTRA_3_THERMOCOUPLE_SELECTED                               3 // Lavagem board only has 1 thermocouple slot but the oven board can have 4

#define COLD_JUNCTION_LOW_TEMPERATURE                              -10.0f
#define COLD_JUNCTION_HIGH_TEMPERATURE                              80.0f

#define THERMOCOUPLE_LOW_TEMPERATURE                               -10.0f
#define THERMOCOUPLE_HIGH_TEMPERATURE                               320.0f //50.0f //320.0f

#define UNREALISTIC_LOW_TEMPERATURE                                -100.0f
#define UNREALISTIC_HIGH_TEMPERATURE                                1000.0f

#define COOLING_FAN_OVERRIDE_TEMPERATURE                            40.0f
#define FORCED_VENTILATION_TEMPERATURE                              150.0f //48.0f //150.0f

#define OUTPUT_FORCED_VENTILATION_STATE                             0b00101001 // Everything off except vapor output and motor
#define FIRMWARE_FORCED_VENTILATION_TIME                            1800000

#define RESISTOR_ON_VENTILATION_OFF_ERROR_DELAY                     10000

#define RESISTOR_ON_ERROR_TEMPERATURE                               50.0f
#define RESISTOR_ON_TEMEPERATURE_ERROR_DELAY                        120000
#define RESISTOR_ON_THRESHOLD_TEMPERATURE                           2.0f

extern Adafruit_MAX31856 thermocoupleConverter;

typedef union
{
    // Byte array that represents the float value of the temperature
    uint8_t byteArray[sizeof(float)] = { 0b00000000 , 0b00000000 , 0b00000000 , 0b00000000 };

    // Float value for the temperature
    float floatValue;
}
temperatureValueTCUnion;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#endif
