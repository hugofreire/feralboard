# Feralboard Pin Map (Firmware-Derived)

This map reflects active definitions in `src/config/Definitions.h`.

## MCU Pins

| Pin | Name | Direction | Function |
| --- | --- | --- | --- |
| 0 | `UART0_DEFAULT_TX_PIN` | Output | Debug UART TX |
| 1 | `UART0_DEFAULT_RX_PIN` | Input | Debug UART RX |
| 2 | `SDA_PIN` | I2C | I2C SDA (DAC) |
| 3 | `SCL_PIN` | I2C | I2C SCL (DAC) |
| 4 | `MOSI_DEFAULT_PIN` | SPI | SPI MOSI |
| 5 | `MISO_DEFAULT_PIN` | SPI | SPI MISO |
| 6 | `SCK_DEFAULT_PIN` | SPI | SPI SCK |
| 8 | `UART3_DEFAULT_TX_PIN` | Output | RS485 UART TX |
| 9 | `UART3_DEFAULT_RX_PIN` | Input | RS485 UART RX |
| 10 | `RS485_DRIVER_ENABLE_PIN` | Output | RS485 TX/RX direction |
| 11 | `RELAY_CONTROLLER_SET_OUTPUTS_PIN` | Output | Shift-register latch |
| 12 | `RELAY_CONTROLLER_ENABLE_PIN` | Output | Shift-register enable |
| 13 | `BUZZER_PIN` | Output (PWM) | Internal alert generator |
| 14 | `ABRIR_CONTROLLER_IN1_PIN` | Output | H-bridge pair A IN1 |
| 15 | `ABRIR_CONTROLLER_IN2_PIN` | Output | H-bridge pair A IN2 |
| 17 | `COOLING_FAN_CONTROL_PIN` | Output | Board cooling control |
| 18 | `UART1_DEFAULT_TX_PIN` | Output | Extra UART TX |
| 19 | `UART1_DEFAULT_RX_PIN` | Input | Extra UART RX |
| 20 | `INPUTS_MUX_CHANNEL_SELECT_3_PIN` | Output | Input mux S3 |
| 21 | `INPUTS_MUX_CHANNEL_SELECT_2_PIN` | Output | Input mux S2 |
| 22 | `INPUTS_MUX_CHANNEL_SELECT_1_PIN` | Output | Input mux S1 |
| 23 | `INPUTS_MUX_CHANNEL_SELECT_0_PIN` | Output | Input mux S0 |
| 24 | `INPUTS_MUX_ENABLE_PIN` | Output | Input mux enable |
| 25 | `INPUTS_MUX_SIGNAL_PIN` | Input | Input mux signal read |
| 26 | `LED_RED_SIGNAL_PIN` | Output | Status LED red |
| 27 | `LED_BLUE_SIGNAL_PIN` | Output | Status LED blue |
| 28 | `THERMOCOUPLE_MUX_ENABLE_PIN` | Output | Thermocouple mux enable |
| 29 | `DATA_READY_THERMOCOUPLE_PIN` | Input | Converter DRDY |
| 30 | `FAULT_THERMOCOUPLE_PIN` | Input | Converter fault |
| 31 | `SSR_A_PIN` | Output | SSR A (defined) |
| 32 | `SSR_B_PIN` | Output | SSR B (defined) |
| 33 | `SSR_C_PIN` | Output | SSR C (defined) |
| 34 | `THERMOCOUPLE_MUX_CHANNEL_SELECT_0_PIN` | Output | Thermocouple mux S0 |
| 35 | `THERMOCOUPLE_MUX_CHANNEL_SELECT_1_PIN` | Output | Thermocouple mux S1 |
| 36 | `SELECT_THERMOCOUPLE_PIN` | Output | Thermocouple converter CS |
| 37 | `STROBE_INPUT_PIN` | Output | Strobe output |
| 38 | `FECHAR_CONTROLLER_IN1_PIN` | Output | H-bridge pair B IN1 |
| 39 | `FECHAR_CONTROLLER_IN2_PIN` | Output | H-bridge pair B IN2 |
| 40 | `RESET_PIN` | Input | MCU reset pin |

## Shift-Register Channels

| Channel | Serial source | Legacy symbol |
| --- | --- | --- |
| `DO0` | byte0.bit0 | `DIRECTION_1_BIT` |
| `DO1` | byte0.bit1 | `DIRECTION_2_BIT` |
| `DO2` | byte0.bit2 | `VELOCIDADE_1_BIT` |
| `DO3` | byte0.bit3 | `VELOCIDADE_2_BIT` |
| `DO4` | byte0.bit4 | `RESISTOR_BIT` |
| `DO5` | byte0.bit5 | `VAPOUR_EXIT_BIT` |
| `DO6` | byte0.bit6 | `EXTRACTOR_BIT` |
| `DO7` | byte0.bit7 | `VAPOR_CREATION_BIT` |
| `DO8` | byte2.bit6 | `OVEN_ILUMINATION_BIT` |
| `DO9` | byte2.bit7 | `BUZZER_EXTERNAL_BIT` |
| `DO10` | byte3.bit0 | `BUZZER_INTERNAL_BIT` |
| `DO11` | byte3.bit1 | `COOLING_FAN_BIT` |

## Multiplexed Input Channels

| Channel | Serial source | Legacy symbol |
| --- | --- | --- |
| `DI0` | byte4.bit0 | `DOOR_END_STOP_BIT` |
| `DI1` | byte4.bit1 | `ELECTRIC_PROTECTION_BIT` |
| `DI2` | byte4.bit2 | `OVEN_OVER_TEMPERATURE_BIT` |
| `DI3` | byte4.bit3 | `MOTOR_OVER_TEMPERATURE_BIT` |
| `DI4` | byte4.bit4 | `DOOR_SWITCH_LOCKED_BIT` |
| `DI5` | byte4.bit5 | `DOOR_SWITCH_LOCKING_1_BIT` |
| `DI6` | byte4.bit6 | `DOOR_SWITCH_LOCKING_2_BIT` |
| `DI7` | byte4.bit7 | `DOOR_SWITCH_TRACTION_BIT` |

## Notes

- Canonical naming is `DI/DO` for new integrations.
- Legacy symbols remain in firmware source for compatibility.
- Full naming guide: see `firmware/IO_NAMING.md`.
