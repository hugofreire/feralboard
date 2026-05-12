# FeralBoard Python SDK - OEM Evaluation Guide

This document describes the customer-facing Python SDK for integrating
FeralBoard into OEM equipment, test fixtures, kiosks, and automation systems.

It is written for technical evaluation. It describes the public API and
integration behavior, but it does not disclose SDK implementation source,
embedded firmware source, or the low-level firmware protocol.

## What The SDK Provides

The FeralBoard Python SDK gives an application controlled access to board I/O:

- Connect to a FeralBoard over a serial device.
- Read digital input channels `DI0` through `DI7`.
- Drive digital output channels `DO0` through `DO11`.
- Clear all outputs to a known safe state.
- Read output echo state when the board reports it.
- Read communication counters for diagnostics.
- Send approved one-shot board commands exposed by the SDK contract.

The recommended customer API is `FeralBoardClient`.

```python
from feralboard_sdk import FeralBoardClient
```

## What Is Not Disclosed

The OEM package is designed to be useful without exposing proprietary internals:

- Firmware source is not included.
- Firmware protocol internals are not included.
- SDK source code is not included in customer deliveries.
- Factory flashing and manufacturing tools are not part of the customer API.

Customers receive documentation, examples, and a versioned SDK package such as a
private wheel:

```bash
pip install feralboard_sdk-0.1.0-py3-none-any.whl
```

## Runtime Requirements

Typical runtime requirements:

- Python 3.9 or newer.
- Linux host with access to the FeralBoard serial device.
- `pyserial`, installed automatically with the SDK package.
- Permission to open the serial device, for example `/dev/ttyAMA0` or
  `/dev/ttyUSB0`.

Only one process should own the FeralBoard serial port at a time. If a GUI,
daemon, or test process already has the port open, stop it before starting a
different control process.

## Quick Start

```python
import time

from feralboard_sdk import FeralBoardClient

with FeralBoardClient("/dev/ttyAMA0") as board:
    board.set_output("DO0", True)
    time.sleep(2)
    board.clear_all_outputs()
```

The context manager connects on entry and clears outputs during disconnect.

## Public API

### `FeralBoardClient(port)`

Creates a client for a serial device path.

```python
board = FeralBoardClient("/dev/ttyAMA0")
```

### `connect() -> bool`

Opens the serial port and starts board communication.

```python
if not board.connect():
    raise RuntimeError("FeralBoard is not available")
```

### `disconnect()`

Clears outputs, stops communication, and closes the serial port.

```python
board.disconnect()
```

### `set_output(channel_name, value)`

Sets a named digital output.

```python
board.set_output("DO3", True)
board.set_output("DO3", False)
```

Valid output channel names are `DO0` through `DO11`.

### `clear_all_outputs()`

Turns off all digital outputs managed by the SDK.

```python
board.clear_all_outputs()
```

Use this in shutdown paths, exception handlers, and operator stop flows.

### `read_input(channel_name) -> bool | None`

Reads a named digital input from the latest valid board state.

```python
door_closed = board.read_input("DI0")
if door_closed is None:
    print("No valid board state yet")
```

Valid input channel names are `DI0` through `DI7`.

`None` means the SDK has not received a valid board state yet.

### `read_output_echo(channel_name) -> bool | None`

Reads the board-reported echo state for an output, when available.

```python
board.set_output("DO0", True)
echo = board.read_output_echo("DO0")
```

`None` means no valid board state is available yet.

### `get_stats() -> tuple[int, int, int]`

Returns communication counters:

```python
tx_count, rx_count, error_count = board.get_stats()
```

These are useful for health checks and diagnostics.

### `send_command_once(command)`

Queues an approved one-shot command exposed by the SDK package.

Use this only for commands documented for your firmware and SDK version.

## Digital I/O Channels

### Digital Inputs

| Channel | Description |
|---------|-------------|
| `DI0` | Digital input 0 |
| `DI1` | Digital input 1 |
| `DI2` | Digital input 2 |
| `DI3` | Digital input 3 |
| `DI4` | Digital input 4 |
| `DI5` | Digital input 5 |
| `DI6` | Digital input 6 |
| `DI7` | Digital input 7 |

### Digital Outputs

| Channel | Description |
|---------|-------------|
| `DO0` | Digital output 0 |
| `DO1` | Digital output 1 |
| `DO2` | Digital output 2 |
| `DO3` | Digital output 3 |
| `DO4` | Digital output 4 |
| `DO5` | Digital output 5 |
| `DO6` | Digital output 6 |
| `DO7` | Digital output 7 |
| `DO8` | Digital output 8 |
| `DO9` | Digital output 9 |
| `DO10` | Digital output 10 |
| `DO11` | Digital output 11 |

Final channel labels and electrical ratings should be taken from the hardware
datasheet for the purchased board revision.

## Timing Model

The SDK maintains board communication in a background thread. Applications set
desired output state through the client, and the SDK sends that state to the
board continuously.

For integration planning:

- Treat I/O as near-real-time control, not hard real-time safety logic.
- Allow a short startup period before relying on input values.
- Use `None` from `read_input()` or `read_output_echo()` as "state not ready".
- Keep one process in charge of the board at a time.

Safety-critical interlocks should be implemented in appropriate hardware or
certified safety controllers, not only in application software.

## Error Handling Pattern

Use `try/finally` or the context manager so outputs are cleared when the
application exits.

```python
from feralboard_sdk import FeralBoardClient

board = FeralBoardClient("/dev/ttyAMA0")

if not board.connect():
    raise SystemExit("FeralBoard is not connected")

try:
    board.set_output("DO0", True)
finally:
    board.clear_all_outputs()
    board.disconnect()
```

## Example Applications

Example scripts are included next to this document:

- `examples/quick_start.py` - connect, set one output, clear outputs.
- `examples/monitor_inputs.py` - print input state changes.
- `examples/output_echo_check.py` - set outputs and check reported echo state.
- `examples/simple_interlock.py` - drive an output based on an input.
- `examples/diagnostics.py` - print communication counters and input snapshots.

Run examples with:

```bash
python examples/quick_start.py --port /dev/ttyAMA0
```

## OEM Evaluation Checklist

Use this checklist to decide whether FeralBoard and the SDK fit your product:

- The host system can run Python 3.9+.
- The host system can access the board serial device.
- Required I/O count fits within `DI0`-`DI7` and `DO0`-`DO11`.
- Application logic can tolerate the SDK background communication model.
- A single software owner can control the board at runtime.
- Your system has a defined safe state and calls `clear_all_outputs()` on exit.
- Any safety-critical behavior is handled outside non-certified application code.

## Versioning And Support Contract

The SDK should be consumed as a versioned binary package. OEM integrations
should pin a tested version:

```bash
pip install feralboard-sdk==0.1.0
```

The public compatibility contract is the documented API in this guide. Internal
implementation details, firmware internals, and undocumented modules may change
between releases.
