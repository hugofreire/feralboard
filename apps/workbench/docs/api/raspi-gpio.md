# raspi-gpio API

TCP GPIO API on the auxiliary Raspberry Pi for E2E test verification.

## Connection

| Parameter | Value |
|-----------|-------|
| Host | `192.168.0.142` |
| Port | `5555` |
| Protocol | TCP, newline-delimited commands |
| SSH alias | `raspi-gpio` |
| Source | `/home/pi/gpio-api/gpio_api.py` on raspi-gpio |

## Commands

All commands are sent as UTF-8 strings terminated with `\n`.

| Command | Response | Description |
|---------|----------|-------------|
| `ping` | `pong` | Health check |
| `read_all` | JSON `{pin: 0/1}` | Read all GPIO pin states |
| `read <pin>` | Single pin value | Read one GPIO pin |
| `write <pin> <0\|1>` | Status string | Set pin as OUTPUT, drive HIGH/LOW |
| `reset <pin>` | Status string | Reset pin to INPUT with pull-up |
| `reset_all` | Status string | Reset all pins to INPUT with pull-up |
| `setup_inputs` | Status string | Configure monitor pins as INPUT |
| `setup_outputs` | Status string | Configure drive pins as OUTPUT |
| `diff <baseline>` | JSON diff | Compare current state vs baseline |

## Pin Assignments

### Monitor Pins (INPUT)

Read FeralBoard output states:

```
GPIO: 0, 1, 5, 6, 7, 8, 11, 12, 13, 16, 19, 20, 21, 26
```

### Drive Pins (OUTPUT)

Simulate FeralBoard input signals:

```
GPIO: 15, 16, 17, 18, 19, 20
```

## GPIO-to-FeralBoard Mappings

### Outputs (FeralBoard DO → raspi-gpio GPIO)

| FeralBoard Output | TX Byte | Bit | GPIO Pin | Direction |
|-------------------|---------|-----|----------|-----------|
| `DO0` (Direction 1) | 0 | 0 | GPIO 12 | HIGH→LOW |
| `DO1` (Direction 2) | 0 | 1 | GPIO 6 | HIGH→LOW |
| `DO2` (Speed 1) | 0 | 2 | GPIO 13 | HIGH→LOW |
| `DO3` (Speed 2) | 0 | 3 | GPIO 16 | HIGH→LOW |
| `DO4` (Resistor) | 0 | 4 | GPIO 19 | HIGH→LOW |
| `DO5` (Vapour Exit) | 0 | 5 | GPIO 20 | HIGH→LOW |
| `DO7` (Vapour Creation) | 0 | 7 | GPIO 21 | HIGH→LOW |

!!! note
    `DO6` (Extractor) does not echo and has no confirmed GPIO mapping.
    `DO8`–`DO11` are internal/on-board outputs with no GPIO connection.

### Inputs (raspi-gpio GPIO → FeralBoard DI)

| GPIO Pin | FeralBoard Input | RX Byte | Bit | Direction |
|----------|------------------|---------|-----|-----------|
| GPIO 15 | `DI0` (Door End Stop) | 4 | 0 | HIGH→LOW (active-low) |
| GPIO 18 | `DI1` (Electric Protection) | 4 | 1 | HIGH→LOW (active-low) |
| GPIO 17 | `DI2` (Oven Over Temp) | 4 | 2 | HIGH→LOW (active-low) |
| GPIO 17 | `DI3` (Motor Over Temp) | 4 | 3 | HIGH→LOW (active-low) |

!!! note
    GPIO 17 maps to both DI2 and DI3 — driving it HIGH toggles both bits.

## Python Usage

```python
from lib.gpio_client import GpioClient

gpio = GpioClient()  # defaults to 192.168.0.142:5555

gpio.ping()           # True if reachable
gpio.read_all()       # {pin: value} dict
gpio.write(15, 1)     # Drive GPIO 15 HIGH
gpio.write(15, 0)     # Drive GPIO 15 LOW
gpio.reset(15)        # Reset to INPUT
gpio.setup_inputs()   # All monitor pins -> INPUT
```

## Hardware Setup

```
FeralBoard  <-->  Flat Cable  <-->  Breadboard  <-->  BSS138 Level Converter  <-->  raspi-gpio
 (5V logic)                                            (3.3V <-> 5V)                (3.3V logic)
```

The SparkFun BSS138 bidirectional level converter bridges the 5V FeralBoard I/O with the 3.3V Raspberry Pi GPIO.
