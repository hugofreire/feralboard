# Serial Protocol

Binary frame format used between the control panel and the FeralBoard controller.

## Overview

| Direction | Frame Size | Description |
|-----------|-----------|-------------|
| Board → Panel | 40 bytes | State frame (outputs echo, inputs, temps, errors) |
| Panel → Board | 11 bytes | Command frame (outputs, commands, CRC8) |

## Communication Parameters

| Parameter | Value |
|-----------|-------|
| Baud rate | `9600` (firmware UART1) |
| Data bits | `8` |
| Parity | `None` |
| Stop bits | `1` |
| Flow control | `None` |
| TX interval | Every 250ms |

!!! note
    The firmware's SERIAL_PROTOCOL.md references 115200 baud, but the actual UART1 communication (used by `board_tester.py` and this project) operates at 9600 baud.

## State Frame (Board → Panel) — 40 bytes

| Byte(s) | Field | Description |
|---------|-------|-------------|
| 0 | Digital Outputs A | `DO0`–`DO7` echo |
| 1 | Reserved | — |
| 2 | Digital Outputs B | `DO8`–`DO9` (bits 6–7) |
| 3 | Digital Outputs C | `DO10`–`DO11` (bits 0–1) |
| 4 | Digital Inputs | `DI0`–`DI7` |
| 5 | Reserved | — |
| 6–9 | Sensor T0 | Float32 LE (main thermocouple) |
| 10–13 | Sensor T1 | Float32 LE |
| 14–17 | Sensor T2 | Float32 LE |
| 18–21 | Sensor T3 | Float32 LE |
| 22 | PCB Temperature | Uint8 (degrees C) |
| 23 | Error Flags | Fault and protection flags |
| 24 | Mode/State | Factory mode (bit 0), door state (bits 6–7) |
| 25 | Module Config | Board configuration byte |
| 26 | Alert Level | 0–255 |
| 27 | Echo Command | Last extra command |
| 28 | Auxiliary Outputs | Optional subsystem outputs echo |
| 29 | Auxiliary Inputs | Optional subsystem input levels |
| 30–33 | Auxiliary Sensor | Float32 LE |
| 34 | Auxiliary PCB Temp | Uint8 |
| 35 | Auxiliary Level | 0–100 (%) |
| 36 | Auxiliary Errors | Optional subsystem faults |
| 37 | Auxiliary Mode | Optional subsystem mode bits |
| 38 | Auxiliary Echo Cmd | Last auxiliary command |
| 39 | Reserved | — |

### Output Echo Bits

#### Byte 0 — `DO0`–`DO7`

| Bit | Channel | Legacy Name |
|-----|---------|-------------|
| 0 | `DO0` | MotorDirectionCCW |
| 1 | `DO1` | MotorDirectionCW |
| 2 | `DO2` | MotorSpeedLow |
| 3 | `DO3` | MotorSpeedHigh |
| 4 | `DO4` | HeaterOn |
| 5 | `DO5` | ReleaseValveOpen |
| 6 | `DO6` | VentilationFanOn |
| 7 | `DO7` | InjectionOn |

#### Byte 2 — `DO8`–`DO9`

| Bit | Channel | Legacy Name |
|-----|---------|-------------|
| 6 | `DO8` | ChamberLightOn |
| 7 | `DO9` | ExternalAlertOn |

#### Byte 3 — `DO10`–`DO11`

| Bit | Channel | Legacy Name |
|-----|---------|-------------|
| 0 | `DO10` | InternalAlertOn |
| 1 | `DO11` | PCBCoolingFanOn |

### Digital Inputs — Byte 4

| Bit | Channel | Legacy Name |
|-----|---------|-------------|
| 0 | `DI0` | ManualDoorClosedSignalOn |
| 1 | `DI1` | MotorProtectionOn |
| 2 | `DI2` | DeviceOverheatSignalOn |
| 3 | `DI3` | MotorOverheatSignalOn |
| 4 | `DI4` | AutomaticSwitchDoorSignal |
| 5 | `DI5` | AutomaticLockSwitchOneSignal |
| 6 | `DI6` | AutomaticLockSwitchTwoSignal |
| 7 | `DI7` | AutomaticSwitchSignal |

### Error Flags — Byte 23

| Bit | Flag |
|-----|------|
| 0 | Electric lock fault |
| 1 | EEPROM / thermocouple over/under voltage |
| 2 | Forced ventilation active |
| 3 | Concurrent outputs / resistor problem |
| 4 | Main thermocouple fault |
| 5 | Main thermocouple high temp |
| 6 | Main thermocouple open circuit |
| 7 | Main thermocouple stuck temp |

### Door State — Byte 24, bits 6–7

| Value | State |
|-------|-------|
| `00` | Unknown |
| `01` | Open |
| `10` | Intermediate |
| `11` | Closed |

## Command Frame (Panel → Board) — 11 bytes

| Byte | Field | Description |
|------|-------|-------------|
| 0 | Digital Outputs A | `DO0`–`DO7` (same bit layout as state byte 0) |
| 1 | Reserved | — |
| 2 | Digital Outputs B | `DO8`–`DO9` (same layout as state byte 2) |
| 3 | Digital Outputs C | `DO10`–`DO11` (same layout as state byte 3) |
| 4 | Command ID | Extra command |
| 5 | Command Data | Command payload |
| 6 | Auxiliary Outputs | Optional auxiliary subsystem |
| 7 | Auxiliary Command | Auxiliary command ID |
| 8 | Auxiliary Data | Auxiliary payload |
| 9 | Origin ID | Source identifier |
| 10 | CRC8 | CRC-8 checksum (bytes 0–9) |

### Command IDs (Byte 4)

| ID | Command | Payload (Byte 5) |
|----|---------|-------------------|
| `0x00` | Default (SetStates) | — |
| `0x01` | GetState | — |
| `0x02` | ResetState | — |
| `0x03` | InvertBit | bit index |
| `0x04` | ResetBitInversion | bit index |
| `0x05` | ServiceMode (FactoryMode) | `0`=off, `1`=on |
| `0x06` | OpenActuator | — |
| `0x07` | CloseActuator | — |
| `0x08` | DirectActuatorControl | control flags |
| `0x09` | ConfigureModule | config byte |
| `0x0A` | SetAlertLevel | 0–255 |
| `0x11` | SetAuxiliaryPercentage | 0–100 |

## CRC-8

- Computed over bytes `0`–`9` of the command frame
- Polynomial: `0x07`
- See `lib/crc8.py` for the lookup table implementation
