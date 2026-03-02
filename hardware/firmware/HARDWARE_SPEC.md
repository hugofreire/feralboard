# Feralboard Hardware Spec (Firmware-Derived)

This document summarizes board I/O capability from the current firmware.

## Summary

- MCU: ATmega4809 (Arduino core).
- Digital outputs: 24 shift-register outputs + direct GPIO control lines.
- Digital inputs: 8 multiplexed digital inputs + thermocouple status lines.
- Sensors: MAX31856 thermocouple converter (4-channel mux), MCP4725 DAC.
- Communications: UART0, UART1, UART3 (RS485), SPI, I2C.

## Digital Outputs

### Shift-register outputs (24 total)

- Byte 0:
  - `DO0` direction bit A
  - `DO1` direction bit B
  - `DO2` speed bit A
  - `DO3` speed bit B
  - `DO4` output channel 4
  - `DO5` output channel 5
  - `DO6` output channel 6
  - `DO7` output channel 7
- Byte 1: currently unused by firmware.
- Byte 2:
  - `DO8` (bit 6)
  - `DO9` (bit 7)
- Byte 3:
  - `DO10` (bit 0)
  - `DO11` (bit 1)

### Direct GPIO outputs

- Internal alert generator (PWM): `BUZZER_PIN`
- Board cooling control: `COOLING_FAN_CONTROL_PIN`
- H-bridge control pair A: `ABRIR_CONTROLLER_IN1_PIN`, `ABRIR_CONTROLLER_IN2_PIN`
- H-bridge control pair B: `FECHAR_CONTROLLER_IN1_PIN`, `FECHAR_CONTROLLER_IN2_PIN`
- Status LEDs: `LED_RED_SIGNAL_PIN`, `LED_BLUE_SIGNAL_PIN`
- Strobe signal: `STROBE_INPUT_PIN`
- Shift-register control: `RELAY_CONTROLLER_SET_OUTPUTS_PIN`, `RELAY_CONTROLLER_ENABLE_PIN`
- RS485 driver enable: `RS485_DRIVER_ENABLE_PIN`

## Digital Inputs

### Multiplexed digital inputs

16-channel mux is defined; channels 0-7 are currently read:
- `DI0` -> mux channel 0
- `DI1` -> mux channel 1
- `DI2` -> mux channel 2
- `DI3` -> mux channel 3
- `DI4` -> mux channel 4
- `DI5` -> mux channel 5
- `DI6` -> mux channel 6
- `DI7` -> mux channel 7

### Thermocouple converter status inputs

- `DATA_READY_THERMOCOUPLE_PIN`
- `FAULT_THERMOCOUPLE_PIN`

## Analog / Sensor

- MAX31856 via SPI:
  - thermocouple values (`T0..T3`)
  - PCB temperature
- MCP4725 via I2C:
  - analog output used by the speed-control path

## Notes

- `SSR_A_PIN`, `SSR_B_PIN`, `SSR_C_PIN` are defined but not currently used in active control logic.
- 14 of 24 shift-register outputs are currently free for expansion.
- Naming reference: see `firmware/IO_NAMING.md`.
