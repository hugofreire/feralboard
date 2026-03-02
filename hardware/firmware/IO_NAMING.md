# Feralboard Generic I/O Naming Manual

This board now uses neutral, multipurpose I/O naming.

## 1) Naming Rules

- Digital inputs are named `DI0..DI7`.
- Digital outputs are named `DO0..DO11` for currently mapped active output bits.
- Use channel names in UI, docs, and new APIs first.
- Avoid domain labels in new code (for example: door, heater, valve, cleaning).
- Legacy fields and command names are kept only for compatibility.

## 2) Input Mapping (`DI`)

All `DI` channels come from state frame byte `4`.

| Channel | Serial Source | Current state field (compatibility) |
| --- | --- | --- |
| `DI0` | byte4.bit0 | `door.manualDoorOpenedSignal` |
| `DI1` | byte4.bit1 | `errors.motorProtection` |
| `DI2` | byte4.bit2 | `errors.deviceOverheatSignal` |
| `DI3` | byte4.bit3 | `errors.motorOverheatSignal` |
| `DI4` | byte4.bit4 | `door.automaticSwitchDoorSignal` |
| `DI5` | byte4.bit5 | `door.automaticLockSwitchOneSignal` |
| `DI6` | byte4.bit6 | `door.automaticLockSwitchTwoSignal` |
| `DI7` | byte4.bit7 | `door.automaticSwitchSignal` |

## 3) Output Mapping (`DO`)

| Channel | Serial Source | Current state field (compatibility) | Command path today |
| --- | --- | --- | --- |
| `DO0` | byte0.bit0 | `motor.direction=counter-clockwise` | `SET_SERVICE_MOTOR_DIRECTION` |
| `DO1` | byte0.bit1 | `motor.direction=clockwise` | `SET_SERVICE_MOTOR_DIRECTION` |
| `DO2` | byte0.bit2 | `motor.speed=low` | `SET_SERVICE_MOTOR_SPEED` |
| `DO3` | byte0.bit3 | `motor.speed=high` | `SET_SERVICE_MOTOR_SPEED` |
| `DO4` | byte0.bit4 | `heater.status` | `SET_SERVICE_HEATER` |
| `DO5` | byte0.bit5 | `releaseValve.status` | `SET_SERVICE_RELEASE_VALVE` |
| `DO6` | byte0.bit6 | `ventilationFan.status` | no dedicated service command |
| `DO7` | byte0.bit7 | `injectionSystem.status` | `SET_SERVICE_INJECTION` |
| `DO8` | byte2.bit6 | `chamberLight.status` | no dedicated service command |
| `DO9` | byte2.bit7 | `alerts.externalBuzzer` | `SET_SERVICE_EXTERNAL_ALERT` |
| `DO10` | byte3.bit0 | `alerts.internalBuzzer` | `SET_SERVICE_INTERNAL_ALERT` |
| `DO11` | byte3.bit1 | PCB cooling fan bit (not exposed in `DeviceState`) | firmware-managed |

## 4) Recommended Labeling

- UI cards/toggles: `DI<n>` and `DO<n>`.
- Optional detailed label format: `DI2 (byte4.bit2)` / `DO9 (byte2.bit7)`.
- For logs: `di2=on`, `do9=off`.

## 5) Compatibility Policy

- Keep old names in internal structures until a full API version cut.
- New docs and new UI features must use `DI/DO` terms.
- If both names are present, `DI/DO` is canonical and legacy names are aliases.
