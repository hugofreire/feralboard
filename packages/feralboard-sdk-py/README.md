# FeralBoard Device SDK

Python SDK for FeralBoard board I/O, firmware deployment, and approved device
management tasks.

## Scope

- Serial protocol constants and helpers
- CRC-8 frame validation
- DI/DO channel maps
- Threaded serial communication client
- High-level board client for named I/O
- Release HEX deployment helper for field updates
- NetworkManager configuration helpers
- Timezone and NTP helpers
- OpenVPN profile and service helpers
- Approved system service controls
- Device identity helpers
- Read-only diagnostics snapshot
- raspi-gpio TCP client used by hardware tests

UI code, kiosk page patterns, pi-web agent logic, and firmware build tooling
stay in their app-specific trees.

## Example

```python
from feralboard_sdk import FeralBoardClient

board = FeralBoardClient("/dev/ttyAMA0")
if board.connect():
    board.set_output("DO0", True)
    board.clear_all_outputs()
    board.disconnect()
```

## Firmware Deployment

The SDK can deploy a supplied release `.hex` file without exposing firmware
source or build tooling:

```python
from feralboard_sdk import deploy_firmware_hex

result = deploy_firmware_hex(
    "feralboard-release.hex",
    port="/dev/ttyAMA3",
    dry_run=True,
)

for command in result.commands:
    print(" ".join(command))
```

## Device Management

Mutating device-management helpers support `dry_run=True` so installers can
validate intended changes before applying them.

```python
from feralboard_sdk import NetworkConfig, apply_network_config

plan = apply_network_config(
    NetworkConfig(
        interface="eth0",
        mode="static",
        ip_address="192.168.10.50",
        prefix=24,
        gateway="192.168.10.1",
        dns=["1.1.1.1"],
    ),
    dry_run=True,
)

for result in plan:
    print(" ".join(result.command))
```
