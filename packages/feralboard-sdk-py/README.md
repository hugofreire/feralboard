# FeralBoard Python SDK

Small Python SDK for the stable FeralBoard board I/O layer.

## Scope

- Serial protocol constants and helpers
- CRC-8 frame validation
- DI/DO channel maps
- Threaded serial communication client
- High-level board client for named I/O
- raspi-gpio TCP client used by hardware tests

UI code, kiosk page patterns, pi-web agent logic, and firmware flashing stay in their app-specific trees.

## Example

```python
from feralboard_sdk import FeralBoardClient

board = FeralBoardClient("/dev/ttyAMA0")
if board.connect():
    board.set_output("DO0", True)
    board.clear_all_outputs()
    board.disconnect()
```
