# FeralBoard Oven Simulator - OEM Evaluation Guide

This document describes the optional FeralBoard Oven Simulator package for OEM
customers building oven-control software.

The simulator is a companion to the FeralBoard Device SDK. It is intentionally
separate from the core SDK because oven behavior is customer-domain specific.
The core SDK remains useful for any FeralBoard product, while this package helps
oven teams develop and validate control-panel logic earlier.

## What It Provides

The oven simulator provides:

- A high-level oven state model.
- Simulated digital inputs for door, protection, and fault signals.
- Simulated digital output echo for control-panel commands.
- Main chamber, lavagem, PCB, and ambient temperature state.
- Basic thermal behavior when the heater output is active.
- Over-temperature and motor/electrical fault simulation.
- A FeralBoard-compatible serial frame loop for software-in-the-loop testing.
- An interactive CLI for manually changing oven state during development.
- Named scenarios for demos, acceptance workshops, and customer onboarding.

The package name is:

```python
import feralboard_oven
```

The CLI entrypoint is:

```bash
feralboard-oven-sim
```

## What Is Not Disclosed

The simulator is designed for application development and customer evaluation
without disclosing proprietary implementation details:

- FeralBoard firmware source is not included.
- Production oven-manager source is not included.
- Firmware build tooling is not included.
- Internal hardware manufacturing tools are not included.
- The simulator is not a certified safety model.

It is a development and evaluation tool, not a replacement for hardware
acceptance testing.

## Recommended Architecture

Use the packages as separate layers:

```text
feralboard_sdk       Generic board I/O, device management, firmware HEX deploy
feralboard_oven      Optional oven simulator and oven-domain development tools
customer app         Oven UI, process logic, recipes, telemetry, integrations
```

This keeps the OEM SDK clean while still giving oven customers a realistic
development path.

## Install

For customer delivery, the package can be shipped as a private wheel:

```bash
pip install feralboard_oven-0.1.0-py3-none-any.whl
```

It depends on `feralboard-sdk` and `pyserial`.

## Basic Python Use

```python
from feralboard_oven import OvenSimulator

sim = OvenSimulator()
sim.set_temperature(180)
sim.set_door_closed(True)

print(sim.snapshot())
```

## Simulated I/O Contract

### Digital Inputs

The simulator exposes oven input conditions through the FeralBoard digital input
model:

| FeralBoard Input | Simulator Meaning |
|------------------|-------------------|
| `DI0` | Door end stop |
| `DI1` | Electric protection OK |
| `DI2` | Oven over-temperature fault |
| `DI3` | Motor over-temperature fault |
| `DI4` | Door switch locked |
| `DI5` | Door switch locking 1 |
| `DI6` | Door switch locking 2 |
| `DI7` | Door switch traction |

### Digital Outputs

The simulator echoes FeralBoard digital output commands and uses selected output
state to drive oven behavior:

| FeralBoard Output | Default Simulator Meaning |
|-------------------|---------------------------|
| `DO0` | Direction 1 |
| `DO1` | Direction 2 |
| `DO2` | Speed 1 |
| `DO3` | Speed 2 |
| `DO4` | Heater / resistor |
| `DO5` | Vapour exit |
| `DO6` | Extractor |
| `DO7` | Vapour creation |
| `DO8` | Oven illumination |
| `DO9` | External buzzer |
| `DO10` | Internal buzzer |
| `DO11` | Cooling fan |

The default thermal model increases main temperature when `DO4` is active and
cools toward ambient temperature when it is inactive. Door-open cooling is
faster than door-closed cooling.

## Serial Simulation

The simulator can serve a serial or PTY path and exchange FeralBoard-compatible
frames with an oven-control process.

Example with a PTY pair:

```bash
socat -d -d pty,raw,echo=0,link=/tmp/feralboard-sim pty,raw,echo=0,link=/tmp/oven-manager
```

Run the simulator on one side:

```bash
feralboard-oven-sim --serial /tmp/feralboard-sim
```

Point the oven manager or customer application at the other side:

```bash
export FERALBOARD_PORT=/tmp/oven-manager
```

This lets the customer run oven logic without a physical FeralBoard attached.

## Interactive CLI

Start the simulator:

```bash
feralboard-oven-sim --serial /tmp/feralboard-sim
```

Interactive commands:

```text
status
temp 180
door open
door closed
fault oven_over_temperature on
fault motor_over_temperature on
fault electric_protection on
fault sensor_fault on
fault oven_over_temperature off
clear
quit
```

The `status` command prints a JSON snapshot with inputs, outputs, temperatures,
door state, and active faults.

## Python Scenario Example

```python
import time

from feralboard_oven import OvenSimulator

sim = OvenSimulator()
sim.set_door_closed(True)
sim.set_temperature(25)

for _ in range(10):
    sim.state.output_echo["DO4"] = True
    sim.advance()
    print(sim.snapshot())
    time.sleep(1)
```

Named scenarios are available for common demos:

```python
from feralboard_oven import door_open, oven_over_temperature, ready_oven

print(ready_oven().snapshot())
print(door_open(temperature_c=90).snapshot())
print(oven_over_temperature().snapshot())
```

## Suggested Customer Evaluation Scenarios

Use these scenarios to evaluate whether the SDK exposes the right behavior for
your oven application:

- Startup with door closed and all faults clear.
- Door open while heater output is requested.
- Heat-up from ambient temperature to a process setpoint.
- Cooldown with door closed and door open.
- Oven over-temperature fault.
- Motor over-temperature fault.
- Electric protection trip.
- Temperature sensor fault.
- Communication interruption between controller and FeralBoard.
- Operator stop path that clears all outputs.
- Recipe step that requires fan direction and speed changes.
- Buzzer and illumination control during alarms.

## Acceptance Questions For The OEM Team

The simulator is a good fit if your team can answer "yes" to these questions:

- Can your oven app treat `DI0`-`DI7` and `DO0`-`DO11` as the hardware I/O API?
- Can your app run against a serial port path supplied by configuration?
- Can your app tolerate simulator timing as software-in-the-loop, not hard
  real-time hardware timing?
- Can your fault and operator-stop flows be validated through input/output state
  changes?
- Can final validation happen on real FeralBoard hardware after simulator
  development?

## Limitations

- The simulator is not a physics-accurate thermal model.
- It does not model every electrical edge case.
- It does not certify safety logic.
- It does not replace hardware-in-the-loop testing.
- Customer-specific recipes, UI, telemetry, and PLC integrations remain in the
  customer application layer.

## Packaging Recommendation

For oven customers, provide two packages:

```text
feralboard-sdk       Device SDK for real board/device control
feralboard-oven      Optional oven simulator and oven-domain tooling
```

This keeps the core SDK general while giving oven teams a practical, friendly
development experience.
